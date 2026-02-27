import pytest
import httpx
import respx
from connectors.walmart import WalmartConnector
from models import Product

MOCK_HTML = """
<html><head></head><body>
<script id="__NEXT_DATA__" type="application/json">
{
  "props": {
    "pageProps": {
      "initialData": {
        "searchResult": {
          "itemStacks": [{
            "items": [
              {
                "priceInfo": {"currentPrice": {"price": 289.00}},
                "availabilityStatusDisplayValue": "In stock",
                "canonicalUrl": "/ip/sony-headphones/123456",
                "name": "Sony WH-1000XM5"
              }
            ]
          }]
        }
      }
    }
  }
}
</script>
</body></html>
"""


@pytest.mark.asyncio
@respx.mock
async def test_walmart_returns_results():
    respx.get(url__startswith="https://www.walmart.com/search").mock(
        return_value=httpx.Response(200, text=MOCK_HTML)
    )
    connector = WalmartConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) == 1
    assert results[0].store == "Walmart"
    assert results[0].price == 289.00
    assert results[0].availability == "In Stock"
    assert "walmart.com" in results[0].url


@pytest.mark.asyncio
@respx.mock
async def test_walmart_returns_empty_when_no_next_data():
    respx.get(url__startswith="https://www.walmart.com/search").mock(
        return_value=httpx.Response(200, text="<html><body>No data</body></html>")
    )
    connector = WalmartConnector()
    results = await connector.search(Product(name="Test"))
    assert results == []
