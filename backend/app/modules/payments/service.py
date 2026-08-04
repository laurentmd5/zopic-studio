from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.modules.payments.models import Order, OrderItem, OrderStatus, PhotoSale
from app.modules.payments.schemas import OrderCreate, OrderResponse
from app.modules.payments.paydunya_client import paydunya_client
from app.modules.competitions.models import Photo, Epreuve, Competition

from app.core.events import event_bus
from app.modules.payments.events import PaymentCompletedEvent

async def create_order(db: AsyncSession, order_data: OrderCreate, user_id: int = None, session_id: str = None) -> OrderResponse:
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
    
    # Group photos by competition to apply packs
    photos_by_comp = {}
    for photo in photos:
        epreuve = epreuves[photo.epreuve_id]
        comp_id = epreuve.competition_id
        if comp_id not in photos_by_comp:
            photos_by_comp[comp_id] = []
        photos_by_comp[comp_id].append(photo)
        
    for comp_id, comp_photos in photos_by_comp.items():
        competition = competitions[comp_id]
        
        # Determine unit price (from settings or fallback)
        settings = competition.settings or {}
        unit_price = settings.get("price_xof", 1500)
        
        photo_count = len(comp_photos)
        comp_total = 0
        
        # Apply packs greedy logic
        if getattr(competition, "packs_enabled", False) and getattr(competition, "packs", None):
            packs = sorted(competition.packs, key=lambda x: x.get("quantity", 0), reverse=True)
            remaining_photos = photo_count
            for pack in packs:
                q = pack.get("quantity", 0)
                p = pack.get("price_xof", 0)
                if q > 0:
                    num_packs = remaining_photos // q
                    comp_total += num_packs * p
                    remaining_photos -= num_packs * q
            comp_total += remaining_photos * unit_price
        else:
            comp_total = photo_count * unit_price
            
        total_amount += comp_total
        
        # For simplicity in OrderItem, distribute the total evenly or just use 0 for some
        # We will just assign the average price to each item for the ledger
        avg_price = comp_total / photo_count if photo_count > 0 else 0
        for photo in comp_photos:
            item = OrderItem(
                photo_id=photo.id,
                price=avg_price
            )
            order_items.append(item)
            
    if total_amount != order_data.amount_expected:
        raise HTTPException(status_code=400, detail=f"Montant transmis invalide. Attendu: {total_amount}, Reçu: {order_data.amount_expected}")
    
    # 2. Créer la commande
    order = Order(
        user_id=user_id,
        session_id=session_id,
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
            photographer_id=competition.photographer_id,
            amount_total=item.price,
            amount_photographer=amount_photographer,

            amount_platform=amount_platform
        )
        db.add(sale)
        
    await db.commit()
    
    # 4. Émettre l'événement métier
    event = PaymentCompletedEvent(
        order_id=order.id,
        session_id=order.session_id,
        user_id=order.user_id
    )
    await event_bus.publish(event)
    
    return {"status": "paid_recorded_and_ledger_created"}
