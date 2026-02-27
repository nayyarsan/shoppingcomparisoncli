import base64
import httpx
from connectors.base import BaseConnector
from models import Product, PriceResult
import config

EBAY_APP_ID = config.EBAY_APP_ID
EBAY_APP_SECRET = config.EBAY_APP_SECRET


class EbayConnector(BaseConnector):
    name = "eBay"
    _TOKEN_URL = "https://api.ebay.com/identity/v1/oauth2/token"
    _SEARCH_URL = "https://api.ebay.com/buy/browse/v1/item_summary/search"

    async def _get_token(self) -> str:
        credentials = base64.b64encode(f"{EBAY_APP_ID}:{EBAY_APP_SECRET}".encode()).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self._TOKEN_URL,
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "grant_type": "client_credentials",
                    "scope": "https://api.ebay.com/oauth/api_scope",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            return resp.json()["access_token"]

    async def search(self, product: Product) -> list[PriceResult]:
        if not EBAY_APP_ID or not EBAY_APP_SECRET:
            return []

        token = await self._get_token()
        query = product.upc or product.name

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self._SEARCH_URL,
                params={
                    "q": query,
                    "limit": 10,
                    "filter": "buyingOptions:{FIXED_PRICE}",
                },
                headers={"Authorization": f"Bearer {token}"},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("itemSummaries", []):
            price_info = item.get("price", {})
            try:
                price = float(price_info.get("value", 0))
            except (ValueError, TypeError):
                continue
            if not price:
                continue
            results.append(PriceResult(
                store=self.name,
                price=price,
                currency=price_info.get("currency", "USD"),
                availability="In Stock",
                url=item.get("itemWebUrl", ""),
                condition=item.get("condition", "Unknown"),
                source="api",
            ))
        return results
