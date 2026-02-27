import httpx
import logging
from models import Product
import config

logger = logging.getLogger(__name__)

GOUPC_API_KEY = config.GOUPC_API_KEY


async def resolve(query: str, upc: str | None = None) -> Product:
    if upc:
        return await _resolve_upc(upc)
    return Product(name=query)


async def _resolve_upc(upc: str) -> Product:
    if not GOUPC_API_KEY:
        return Product(name=upc, upc=upc)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://go-upc.com/api/v1/code/{upc}",
                headers={"Authorization": f"Bearer {GOUPC_API_KEY}"},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            product_data = data.get("product", {})
            return Product(
                name=product_data.get("name", upc),
                upc=upc,
                brand=product_data.get("brand"),
                category=product_data.get("category"),
            )
    except Exception as e:
        logger.warning(f"Go-UPC lookup failed for {upc}: {e}")
        return Product(name=upc, upc=upc)
