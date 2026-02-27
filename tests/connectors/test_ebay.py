import pytest
import httpx
import respx
from connectors.ebay import EbayConnector
from models import Product

MOCK_TOKEN_RESPONSE = {"access_token": "test-token", "token_type": "Application Access Token"}

MOCK_SEARCH_RESPONSE = {
    "itemSummaries": [
        {
            "itemId": "v1|1234|0",
            "title": "Sony WH-1000XM5",
            "price": {"value": "249.00", "currency": "USD"},
            "condition": "New",
            "itemWebUrl": "https://ebay.com/itm/1234",
            "buyingOptions": ["FIXED_PRICE"],
        }
    ]
}


@pytest.mark.asyncio
async def test_ebay_returns_empty_without_credentials(monkeypatch):
    monkeypatch.setattr("connectors.ebay.EBAY_APP_ID", "")
    monkeypatch.setattr("connectors.ebay.EBAY_APP_SECRET", "")
    connector = EbayConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert results == []


@pytest.mark.asyncio
@respx.mock
async def test_ebay_returns_price_results(monkeypatch):
    monkeypatch.setattr("connectors.ebay.EBAY_APP_ID", "test-id")
    monkeypatch.setattr("connectors.ebay.EBAY_APP_SECRET", "test-secret")
    respx.post("https://api.ebay.com/identity/v1/oauth2/token").mock(
        return_value=httpx.Response(200, json=MOCK_TOKEN_RESPONSE)
    )
    respx.get(url__startswith="https://api.ebay.com/buy/browse/v1/item_summary/search").mock(
        return_value=httpx.Response(200, json=MOCK_SEARCH_RESPONSE)
    )
    connector = EbayConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) == 1
    assert results[0].store == "eBay"
    assert results[0].price == 249.00
    assert results[0].url == "https://ebay.com/itm/1234"
