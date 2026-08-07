from app.modules.payments.pricing import calculate_order_items
from app.modules.competitions.models import Photo, Epreuve, Competition

def test_calculate_order_items_no_packs():
    photos = [
        Photo(id=1, epreuve_id=1),
        Photo(id=2, epreuve_id=1),
    ]
    epreuves = {1: Epreuve(id=1, competition_id=1)}
    competitions = {1: Competition(id=1, settings={"price_xof": 1500}, packs_enabled=False)}

    total_amount, order_items = calculate_order_items(photos, epreuves, competitions)
    
    assert total_amount == 3000
    assert len(order_items) == 2
    assert order_items[0].price == 1500
    assert order_items[1].price == 1500

def test_calculate_order_items_with_packs():
    photos = [
        Photo(id=i, epreuve_id=1) for i in range(1, 12)
    ] # 11 photos
    epreuves = {1: Epreuve(id=1, competition_id=1)}
    competitions = {
        1: Competition(
            id=1, 
            settings={"price_xof": 1500}, 
            packs_enabled=True,
            packs=[
                {"quantity": 10, "price_xof": 3500},
                {"quantity": 5, "price_xof": 2000}
            ]
        )
    }

    # 11 photos = 1 pack of 10 (3500) + 1 single (1500) = 5000 FCFA
    total_amount, order_items = calculate_order_items(photos, epreuves, competitions)
    
    assert total_amount == 5000
    assert len(order_items) == 11
    
    # Check that sum of item prices equals total_amount
    assert sum(item.price for item in order_items) == 5000
    
    # Base price should be 5000 // 11 = 454
    # Remainder is 5000 % 11 = 6
    # 6 items get 455, 5 items get 454
    prices = [item.price for item in order_items]
    assert prices.count(455) == 6
    assert prices.count(454) == 5

def test_calculate_order_items_remainder_distribution():
    photos = [
        Photo(id=i, epreuve_id=1) for i in range(1, 4)
    ] # 3 photos
    epreuves = {1: Epreuve(id=1, competition_id=1)}
    competitions = {
        1: Competition(
            id=1, 
            settings={"price_xof": 1500}, 
            packs_enabled=True,
            packs=[{"quantity": 3, "price_xof": 2000}]
        )
    }

    # 3 photos = 1 pack of 3 (2000) = 2000 FCFA
    total_amount, order_items = calculate_order_items(photos, epreuves, competitions)
    
    assert total_amount == 2000
    
    # 2000 // 3 = 666, remainder 2
    # 2 items at 667, 1 item at 666
    prices = [item.price for item in order_items]
    assert prices.count(667) == 2
    assert prices.count(666) == 1
    assert sum(prices) == 2000
