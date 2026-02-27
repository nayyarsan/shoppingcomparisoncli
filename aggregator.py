import asyncio
import logging
from models import Product, PriceResult
from connectors.base import BaseConnector

logger = logging.getLogger(__name__)


async def run_all(product: Product, connectors: list[BaseConnector]) -> list[PriceResult]:
    tasks = [_safe_search(c, product) for c in connectors]
    results = await asyncio.gather(*tasks)
    flat = [r for sublist in results for r in sublist]
    return sorted(flat, key=lambda r: r.price)


async def _safe_search(connector: BaseConnector, product: Product) -> list[PriceResult]:
    try:
        return await connector.search(product)
    except Exception as e:
        logger.warning(f"[{connector.name}] failed: {e}")
        return []
