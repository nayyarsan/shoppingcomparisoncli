from abc import ABC, abstractmethod
from models import Product, PriceResult


class BaseConnector(ABC):
    name: str = "Base"

    @abstractmethod
    async def search(self, product: Product) -> list[PriceResult]:
        pass
