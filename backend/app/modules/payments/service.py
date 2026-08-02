from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.modules.payments.models import Order, OrderItem, OrderStatus, PhotoSale
from app.modules.payments.schemas import OrderCreate, OrderResponse
from app.modules.payments.paydunya_client import paydunya_client
from app.modules.competitions.models import Photo, Epreuve, Competition

async def create_order(db: AsyncSession, order_data: OrderCreate, user_id: int = None) -> OrderResponse:
    # 1. RÃ©cupÃ©rer toutes les photos pour calculer le total
    result = await db.execute(select(Photo).where(Photo.id.in_(order_data.photo_ids)))
    photos = result.scalars().all()
    
    if len(photos) != len(order_data.photo_ids):
        raise HTTPException(status_code=400, detail="Certaines photos n'ont pas Ã©tÃ© trouvÃ©es.")

    total_amount = 0
    # On rÃ©cupÃ¨re les prix des epreuves
    album_ids = list(set([photo.epreuve_id for photo in photos]))
    albums_result = await db.execute(select(Epreuve).where(Epreuve.id.in_(album_ids)))
    epreuves = {epreuve.id: epreuve for epreuve in albums_result.scalars().all()}
    
    # On doit aussi rÃ©cupÃ©rer les competition pour connaÃ®tre le photographe et potentiellement le prix si configurÃ© au niveau competition
    event_ids = list(set([epreuve.competition_id for epreuve in epreuves.values()]))
    events_result = await db.execute(select(Competition).where(Competition.id.in_(event_ids)))
    competitions = {competition.id: competition for competition in events_result.scalars().all()}
    
    order_items = []
    
    for photo in photos:
        epreuve = epreuves[photo.epreuve_id]
        competition = competitions[epreuve.competition_id]
        
        # Supposons qu'il y ait une colonne price_per_photo dans Competition
        # Sinon, pour le MVP, on utilise un prix fixe de 500 FCFA
        price = getattr(competition, 'price_per_photo', 500)
        
        total_amount += price
        
        item = OrderItem(
            photo_id=photo.id,
            price=price
        )
        order_items.append(item)
    
    # 2. CrÃ©er la commande
    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status=OrderStatus.PENDING
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    
    # Ajouter les items
    for item in order_items:
        item.order_id = order.id
        db.add(item)
    await db.commit()
    
    # 3. Appeler PayDunya
    invoice = await paydunya_client.create_invoice(
        amount=total_amount,
        order_id=order.id,
        cancel_url=order_data.cancel_url,
        return_url=order_data.return_url
    )
    
    # Mettre Ã  jour le token
    order.paydunya_token = invoice["token"]
    await db.commit()
    
    return OrderResponse(
        order_id=order.id,
        total_amount=total_amount,
        paydunya_token=invoice["token"],
        payment_url=invoice["payment_url"]
    )

async def process_webhook(db: AsyncSession, token: str, is_success: bool = True):
    # RÃ©cupÃ©rer la commande
    result = await db.execute(select(Order).where(Order.paydunya_token == token))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable.")
        
    if order.status != OrderStatus.PENDING:
        return {"status": "already_processed"}
        
    if not is_success:
        order.status = OrderStatus.FAILED
        await db.commit()
        return {"status": "failed_recorded"}
        
    # SuccÃ¨s !
    order.status = OrderStatus.PAID
    await db.commit()
    
    # CrÃ©ation du ledger (PhotoSale)
    result = await db.execute(select(OrderItem).where(OrderItem.order_id == order.id))
    items = result.scalars().all()
    
    for item in items:
        # RÃ©cupÃ©rer la photo pour avoir le photographer_id via l'competition
        photo_res = await db.execute(select(Photo).where(Photo.id == item.photo_id))
        photo = photo_res.scalars().first()
        album_res = await db.execute(select(Epreuve).where(Epreuve.id == photo.epreuve_id))
        epreuve = album_res.scalars().first()
        event_res = await db.execute(select(Competition).where(Competition.id == epreuve.competition_id))
        competition = event_res.scalars().first()
        
        # Split : 25% plateforme, 75% photographe
        amount_platform = int(item.price * 0.25)
        amount_photographer = item.price - amount_platform
        
        sale = PhotoSale(
            order_item_id=item.id,
            photographer_id=competition.user_id,
            amount_total=item.price,
            amount_photographer=amount_photographer,
            amount_platform=amount_platform
        )
        db.add(sale)
        
    await db.commit()
    return {"status": "paid_recorded_and_ledger_created"}
