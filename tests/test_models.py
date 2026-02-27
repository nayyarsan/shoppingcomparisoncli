from models import Product, PriceResult


def test_product_minimal():
    p = Product(name="Sony WH-1000XM5")
    assert p.name == "Sony WH-1000XM5"
    assert p.upc is None
    assert p.brand is None
    assert p.category is None


def test_product_full():
    p = Product(name="Sony WH-1000XM5", upc="027242920859", brand="Sony", category="Headphones")
    assert p.upc == "027242920859"
    assert p.brand == "Sony"


def test_price_result_defaults():
    r = PriceResult(store="Best Buy", price=279.99)
    assert r.currency == "USD"
    assert r.availability == "Unknown"
    assert r.condition == "New"
    assert r.source == "api"
    assert r.url == ""


def test_price_result_full():
    r = PriceResult(
        store="eBay", price=249.00, currency="USD",
        availability="In Stock", url="https://ebay.com/1",
        condition="Used", source="api"
    )
    assert r.condition == "Used"
