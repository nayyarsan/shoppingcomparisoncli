import pytest
from typer.testing import CliRunner
from unittest.mock import AsyncMock, patch
from main import app
from models import Product, PriceResult

runner = CliRunner()


@pytest.fixture
def mock_connectors():
    mock = AsyncMock()
    mock.search.return_value = [
        PriceResult(store="Best Buy", price=279.99, url="https://bestbuy.com/1")
    ]
    mock.name = "Best Buy"
    return [mock]


def test_search_by_name_exits_successfully(mock_connectors):
    with patch("main.CONNECTORS", mock_connectors), \
         patch("main.resolve", AsyncMock(return_value=Product(name="Sony WH-1000XM5"))), \
         patch("main.run_all", AsyncMock(return_value=[PriceResult(store="Best Buy", price=279.99)])), \
         patch("main.save", return_value=(None, None)):
        result = runner.invoke(app, ["Sony WH-1000XM5"])
    assert result.exit_code == 0


def test_search_with_upc_flag(mock_connectors):
    with patch("main.CONNECTORS", mock_connectors), \
         patch("main.resolve", AsyncMock(return_value=Product(name="Sony WH-1000XM5", upc="027242920859"))), \
         patch("main.run_all", AsyncMock(return_value=[])), \
         patch("main.save", return_value=(None, None)):
        result = runner.invoke(app, ["--upc", "027242920859"])
    assert result.exit_code == 0


def test_search_shows_no_results_message():
    with patch("main.resolve", AsyncMock(return_value=Product(name="NonExistentProduct999"))), \
         patch("main.run_all", AsyncMock(return_value=[])), \
         patch("main.save", return_value=(None, None)):
        result = runner.invoke(app, ["NonExistentProduct999"])
    assert result.exit_code == 0
