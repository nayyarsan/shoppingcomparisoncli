import re
import json
import httpx
from connectors.base import BaseConnector
from models import Product, PriceResult


class WalmartConnector(BaseConnector):
    name = "Walmart"
    _SEARCH_URL = "https://www.walmart.com/search"
    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    async def search(self, product: Product) -> list[PriceResult]:
        query = product.upc or product.name
        async with httpx.AsyncClient(headers=self._HEADERS, follow_redirects=True) as client:
            resp = await client.get(
                self._SEARCH_URL,
                params={"q": query},
                timeout=15.0,
            )
            resp.raise_for_status()

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            resp.text,
            re.DOTALL,
        )
        if not match:
            return []

        try:
            data = json.loads(match.group(1))
            items = (
                data["props"]["pageProps"]["initialData"]
                ["searchResult"]["itemStacks"][0]["items"]
            )
        except (KeyError, IndexError, json.JSONDecodeError):
            return []

        results = []
        for item in items[:10]:
            price = (item.get("priceInfo") or {}).get("currentPrice", {}).get("price")
            if not price:
                continue
            avail_raw = item.get("availabilityStatusDisplayValue", "")
            availability = "In Stock" if "in stock" in avail_raw.lower() else "Unknown"
            canonical = item.get("canonicalUrl", "")
            results.append(PriceResult(
                store=self.name,
                price=float(price),
                availability=availability,
                url=f"https://www.walmart.com{canonical}",
                condition="New",
                source="scrape",
            ))
        return results
