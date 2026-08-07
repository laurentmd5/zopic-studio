from typing import List, Dict, Any
from app.modules.payments.models import OrderItem
from app.modules.competitions.models import Photo, Epreuve, Competition

def calculate_order_items(photos: List[Photo], epreuves: Dict[int, Epreuve], competitions: Dict[int, Competition]) -> tuple[int, List[OrderItem]]:
    """
    Calcule le total de la commande et génère les OrderItem avec la logique de packs (Glouton).
    Retourne (total_amount, order_items).
    """
    total_amount = 0
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
        
        # For simplicity in OrderItem, distribute the total exactly
        if photo_count > 0:
            base_price = int(comp_total // photo_count)
            remainder = int(comp_total % photo_count)
            for i, photo in enumerate(comp_photos):
                item_price = base_price + (1 if i < remainder else 0)
                item = OrderItem(
                    photo_id=photo.id,
                    price=item_price
                )
                order_items.append(item)
                
    return total_amount, order_items
