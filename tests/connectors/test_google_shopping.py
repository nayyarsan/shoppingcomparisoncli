import pytest
import httpx
import respx
from connectors.google_shopping import GoogleShoppingConnector
from models import Product

MOCK_RESPONSE = {
    "shopping_results": [
        {
            "title": "Sony WH-1000XM5",
            "price": "$279.99",
            "source": "Walmart",
            "link": "https://walmart.com/product/1",
            "condition": "new",
        },
        {
            "title": "Sony WH-1000XM5",
            "price": "$289.00",
            "source": "Target",
            "link": "https://target.com/product/1",
            "condition": "new",
        },
    ]
}


@pytest.mark.asyncio
async def test_google_shopping_returns_empty_without_key(monkeypatch):
    monkeypatch.setattr("connectors.google_shopping.SERPAPI_API_KEY", "")
    connector = GoogleShoppingConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_google_shopping_returns_results(monkeypatch):
    monkeypatch.setattr("connectors.google_shopping.SERPAPI_API_KEY", "test-key")
    respx.get(url__startswith="https://serpapi.com/search").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    connector = GoogleShoppingConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) == 2
    assert results[0].store == "Walmart"
    assert results[0].price == 279.99
    assert results[1].store == "Target"


@pytest.mark.asyncio
@respx.mock
async def test_google_shopping_skips_unparseable_prices(monkeypatch):
    monkeypatch.setattr("connectors.google_shopping.SERPAPI_API_KEY", "test-key")
    respx.get(url__startswith="https://serpapi.com/search").mock(
        return_value=httpx.Response(200, json={
            "shopping_results": [
                {"title": "X", "price": "Call for price", "source": "SomeStore", "link": ""},
                {"title": "Y", "price": "$99.99", "source": "AnotherStore", "link": "https://example.com"},
            ]
        })
    )
    connector = GoogleShoppingConnector()
    results = await connector.search(Product(name="Test"))
    assert len(results) == 1
    assert results[0].price == 99.99
