import pytest
from unittest.mock import AsyncMock
from aggregator import run_all
from models import Product, PriceResult
from connectors.base import BaseConnector


def make_connector(name: str, results: list[PriceResult], fail: bool = False) -> BaseConnector:
    mock = AsyncMock(spec=BaseConnector)
    mock.name = name
    if fail:
        mock.search.side_effect = Exception("Network error")
    else:
        mock.search.return_value = results
    return mock


@pytest.mark.asyncio
async def test_aggregator_collects_all_results():
    product = Product(name="Test Product")
    c1 = make_connector("Store1", [PriceResult(store="Store1", price=299.99)])
    c2 = make_connector("Store2", [PriceResult(store="Store2", price=249.99)])
    results = await run_all(product, [c1, c2])
    assert len(results) == 2


@pytest.mark.asyncio
async def test_aggregator_sorts_by_price_ascending():
    product = Product(name="Test Product")
    c1 = make_connector("Store1", [PriceResult(store="Store1", price=299.99)])
    c2 = make_connector("Store2", [PriceResult(store="Store2", price=249.99)])
    results = await run_all(product, [c1, c2])
    assert results[0].price == 249.99
    assert results[1].price == 299.99


@pytest.mark.asyncio
async def test_aggregator_handles_connector_failure():
    product = Product(name="Test Product")
    failing = make_connector("BadStore", [], fail=True)
    working = make_connector("GoodStore", [PriceResult(store="GoodStore", price=199.99)])
    results = await run_all(product, [failing, working])
    assert len(results) == 1
    assert results[0].store == "GoodStore"


@pytest.mark.asyncio
async def test_aggregator_returns_empty_when_all_fail():
    product = Product(name="Test Product")
    c1 = make_connector("Store1", [], fail=True)
    c2 = make_connector("Store2", [], fail=True)
    results = await run_all(product, [c1, c2])
    assert results == []
