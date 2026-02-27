import httpx
from connectors.base import BaseConnector
from models import Product, PriceResult
import config

SERPAPI_API_KEY = config.SERPAPI_API_KEY


class GoogleShoppingConnector(BaseConnector):
    name = "Google Shopping"
    _SEARCH_URL = "https://serpapi.com/search"

    async def search(self, product: Product) -> list[PriceResult]:
        if not SERPAPI_API_KEY:
            return []

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self._SEARCH_URL,
                params={
                    "engine": "google_shopping",
                    "q": product.name,
                    "api_key": SERPAPI_API_KEY,
                    "gl": "us",
                    "hl": "en",
                    "num": 20,
                },
                timeout=20.0,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("shopping_results", []):
            price_str = item.get("price", "")
            try:
                price = float(price_str.replace("$", "").replace(",", "").strip())
            except (ValueError, AttributeError):
                continue
            results.append(PriceResult(
                store=item.get("source", "Unknown"),
                price=price,
                availability="Unknown",
                url=item.get("link", ""),
                condition=item.get("condition", "New"),
                source="api",
            ))
        return results
