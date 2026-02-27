import pytest
import httpx
import respx
from connectors.bestbuy import BestBuyConnector
from models import Product

MOCK_RESPONSE = {
    "products": [
        {
            "name": "Sony WH-1000XM5",
            "salePrice": 279.99,
            "availability": "Available",
            "availabilityType": "InStore",
            "url": "https://bestbuy.com/product/1",
            "condition": "New",
        }
    ]
}


@pytest.mark.asyncio
async def test_bestbuy_returns_empty_without_api_key(monkeypatch):
    monkeypatch.setattr("connectors.bestbuy.BESTBUY_API_KEY", "")
    connector = BestBuyConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_bestbuy_returns_price_results(monkeypatch):
    monkeypatch.setattr("connectors.bestbuy.BESTBUY_API_KEY", "test-key")
    respx.get(url__startswith="https://api.bestbuy.com/v1/products").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    connector = BestBuyConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) == 1
    assert results[0].store == "Best Buy"
    assert results[0].price == 279.99
    assert results[0].condition == "New"


@pytest.mark.asyncio
@respx.mock
async def test_bestbuy_uses_upc_when_available(monkeypatch):
    monkeypatch.setattr("connectors.bestbuy.BESTBUY_API_KEY", "test-key")
    route = respx.get(url__startswith="https://api.bestbuy.com/v1/products(upc=027242920859)").mock(
        return_value=httpx.Response(200, json=MOCK_RESPONSE)
    )
    connector = BestBuyConnector()
    await connector.search(Product(name="Sony", upc="027242920859"))
    assert route.called


@pytest.mark.asyncio
@respx.mock
async def test_bestbuy_handles_api_error(monkeypatch):
    monkeypatch.setattr("connectors.bestbuy.BESTBUY_API_KEY", "test-key")
    respx.get(url__startswith="https://api.bestbuy.com").mock(
        return_value=httpx.Response(403)
    )
    connector = BestBuyConnector()
    with pytest.raises(Exception):
        await connector.search(Product(name="Test"))
