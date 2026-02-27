import json
import csv
import pytest
from pathlib import Path
from formatter import save
from models import Product, PriceResult


@pytest.fixture
def sample_results():
    return [
        PriceResult(store="Best Buy", price=279.99, availability="In Stock", url="https://bestbuy.com/1"),
        PriceResult(store="eBay", price=249.00, condition="Used", url="https://ebay.com/2"),
    ]


def test_save_creates_json_file(tmp_path, monkeypatch, sample_results):
    monkeypatch.chdir(tmp_path)
    product = Product(name="Sony WH-1000XM5")
    json_path, _ = save(product, sample_results)
    assert json_path.exists()


def test_save_creates_csv_file(tmp_path, monkeypatch, sample_results):
    monkeypatch.chdir(tmp_path)
    product = Product(name="Sony WH-1000XM5")
    _, csv_path = save(product, sample_results)
    assert csv_path.exists()


def test_save_json_contains_all_results(tmp_path, monkeypatch, sample_results):
    monkeypatch.chdir(tmp_path)
    product = Product(name="Sony WH-1000XM5")
    json_path, _ = save(product, sample_results)
    data = json.loads(json_path.read_text())
    assert len(data) == 2
    assert data[0]["store"] == "Best Buy"
    assert data[0]["price"] == 279.99


def test_save_csv_contains_all_results(tmp_path, monkeypatch, sample_results):
    monkeypatch.chdir(tmp_path)
    product = Product(name="Sony WH-1000XM5")
    _, csv_path = save(product, sample_results)
    with csv_path.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[1]["condition"] == "Used"


def test_save_filename_uses_slug_and_date(tmp_path, monkeypatch, sample_results):
    monkeypatch.chdir(tmp_path)
    product = Product(name="Sony WH-1000XM5")
    json_path, _ = save(product, sample_results)
    assert "sony-wh-1000xm5" in json_path.name
