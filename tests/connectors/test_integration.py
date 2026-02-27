"""
Integration tests — hit the real APIs.

Run with:
    pytest tests/connectors/test_integration.py -v -s

Each test is skipped automatically if the required API key is absent from .env.
Set up your .env file first (copy .env.example and fill in your keys).
"""
import os
import pytest
from models import Product


# ---------------------------------------------------------------------------
# Best Buy
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("BESTBUY_API_KEY"), reason="BESTBUY_API_KEY not set")
async def test_bestbuy_live():
    from connectors.bestbuy import BestBuyConnector
    connector = BestBuyConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) > 0, "Expected at least one result from Best Buy"
    assert all(r.store == "Best Buy" for r in results)
    assert all(r.price > 0 for r in results)
    print(f"\n[Best Buy] {len(results)} results, cheapest: ${results[0].price:.2f}")


# ---------------------------------------------------------------------------
# eBay
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(
    not (os.getenv("EBAY_APP_ID") and os.getenv("EBAY_APP_SECRET")),
    reason="EBAY_APP_ID / EBAY_APP_SECRET not set",
)
async def test_ebay_live():
    from connectors.ebay import EbayConnector
    connector = EbayConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) > 0, "Expected at least one result from eBay"
    assert all(r.store == "eBay" for r in results)
    assert all(r.price > 0 for r in results)
    print(f"\n[eBay] {len(results)} results, cheapest: ${results[0].price:.2f}")


# ---------------------------------------------------------------------------
# Google Shopping (SerpAPI)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("SERPAPI_API_KEY"), reason="SERPAPI_API_KEY not set")
async def test_google_shopping_live():
    from connectors.google_shopping import GoogleShoppingConnector
    connector = GoogleShoppingConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    assert len(results) > 0, "Expected at least one result from Google Shopping"
    assert all(r.price > 0 for r in results)
    stores = {r.store for r in results}
    print(f"\n[Google Shopping] {len(results)} results across stores: {stores}")


# ---------------------------------------------------------------------------
# Walmart (scraping — no key required)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_walmart_live():
    from connectors.walmart import WalmartConnector
    connector = WalmartConnector()
    results = await connector.search(Product(name="Sony WH-1000XM5"))
    # Walmart scraping may be blocked; just verify it doesn't crash
    assert isinstance(results, list)
    if results:
        assert all(r.store == "Walmart" for r in results)
        assert all(r.price > 0 for r in results)
        print(f"\n[Walmart] {len(results)} results, cheapest: ${results[0].price:.2f}")
    else:
        print("\n[Walmart] No results (may be blocked by anti-scraping)")


# ---------------------------------------------------------------------------
# UPC resolver (Go-UPC)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("GOUPC_API_KEY"), reason="GOUPC_API_KEY not set")
async def test_resolver_upc_live():
    from resolver import resolve
    product = await resolve("", upc="027242920859")
    assert product.upc == "027242920859"
    assert product.name != "027242920859", "Expected Go-UPC to return a real product name"
    print(f"\n[Go-UPC] Resolved: {product.name} by {product.brand}")
