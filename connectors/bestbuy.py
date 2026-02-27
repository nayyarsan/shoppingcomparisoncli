import httpx
from connectors.base import BaseConnector
from models import Product, PriceResult
import config

BESTBUY_API_KEY = config.BESTBUY_API_KEY


class BestBuyConnector(BaseConnector):
    name = "Best Buy"
    _BASE_URL = "https://api.bestbuy.com/v1/products"

    async def search(self, product: Product) -> list[PriceResult]:
        if not BESTBUY_API_KEY:
            return []

        search_filter = f"(upc={product.upc})" if product.upc else f"(search={product.name})"

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self._BASE_URL}{search_filter}",
                params={
                    "format": "json",
                    "show": "name,salePrice,regularPrice,availability,availabilityType,url,condition,upc",
                    "pageSize": 10,
                    "apiKey": BESTBUY_API_KEY,
                },
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("products", []):
            price = item.get("salePrice") or item.get("regularPrice", 0)
            if not price:
                continue
            avail_type = item.get("availabilityType", "")
            availability = "In Stock" if avail_type in ("InStore", "Online") else item.get("availability", "Unknown")
            results.append(PriceResult(
                store=self.name,
                price=float(price),
                availability=availability,
                url=item.get("url", ""),
                condition=item.get("condition", "New"),
                source="api",
            ))
        return results
