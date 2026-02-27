import pytest
import httpx
import respx
from resolver import resolve
from models import Product


@pytest.mark.asyncio
async def test_resolve_by_name_returns_product():
    product = await resolve("Sony WH-1000XM5")
    assert product.name == "Sony WH-1000XM5"
    assert product.upc is None


@pytest.mark.asyncio
async def test_resolve_upc_without_api_key(monkeypatch):
    monkeypatch.setattr("resolver.GOUPC_API_KEY", "")
    product = await resolve("", upc="027242920859")
    assert product.upc == "027242920859"
    assert product.name == "027242920859"


@pytest.mark.asyncio
@respx.mock
async def test_resolve_upc_with_api_key(monkeypatch):
    monkeypatch.setattr("resolver.GOUPC_API_KEY", "test-key")
    respx.get("https://go-upc.com/api/v1/code/027242920859").mock(
        return_value=httpx.Response(200, json={
            "product": {
                "name": "Sony WH-1000XM5",
                "brand": "Sony",
                "category": "Headphones"
            }
        })
    )
    product = await resolve("", upc="027242920859")
    assert product.name == "Sony WH-1000XM5"
    assert product.brand == "Sony"
    assert product.upc == "027242920859"


@pytest.mark.asyncio
@respx.mock
async def test_resolve_upc_api_failure_falls_back(monkeypatch):
    monkeypatch.setattr("resolver.GOUPC_API_KEY", "test-key")
    respx.get("https://go-upc.com/api/v1/code/000000000000").mock(
        return_value=httpx.Response(404)
    )
    product = await resolve("", upc="000000000000")
    assert product.upc == "000000000000"
