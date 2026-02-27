from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    name: str
    upc: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None


@dataclass
class PriceResult:
    store: str
    price: float
    currency: str = "USD"
    availability: str = "Unknown"
    url: str = ""
    condition: str = "New"
    source: str = "api"
