# Shopping Agent

A CLI tool that accepts a product name or UPC/barcode and returns a price comparison across US retail stores. Output is shown as a rich terminal table and saved as JSON + CSV files in `./results/`.

## Features

- Search by product name or UPC/barcode
- Parallel queries across Best Buy, eBay, Walmart, and 20+ stores via Google Shopping
- Fault-tolerant: if one store fails, the rest continue
- Results sorted by price (cheapest first)
- Saves JSON + CSV to `./results/` automatically

## Quickstart

### 1. Clone and install

```bash
git clone <repo-url>
cd shoppingagent
pip install -r requirements.txt
```

### 2. Set up API keys

```bash
cp .env.example .env
# Open .env and fill in your keys (see "API Keys" section below)
```

### 3. Run

```bash
# Search by product name
python main.py "Sony WH-1000XM5"

# Search by UPC/barcode
python main.py --upc 027242920859

# Help
python main.py --help
```

## Sample Output

```
Searching for: Sony WH-1000XM5 Headphones
Found 12 results across 5 stores

┌──────────────┬──────────┬─────────────┬────────────────────────────┐
│ Store        │ Price    │ Condition   │ URL                        │
├──────────────┼──────────┼─────────────┼────────────────────────────┤
│ eBay         │ $249.00  │ Used        │ ebay.com/...               │
│ Best Buy     │ $279.99  │ New         │ bestbuy.com/...            │
│ Walmart      │ $289.00  │ New         │ walmart.com/...            │
│ Walmart      │ $299.00  │ New         │ store.example.com/...      │
└──────────────┴──────────┴─────────────┴────────────────────────────┘

Saved to results/sony-wh-1000xm5-2026-02-26.json
Saved to results/sony-wh-1000xm5-2026-02-26.csv
```

## API Keys

All keys are free tier. Copy `.env.example` to `.env` and fill in each one.

### Go-UPC (barcode → product name)
- **Required for:** `--upc` flag (without it, UPC is used as the product name)
- **Sign up:** https://go-upc.com/api
- **Free tier:** limited lookups/month
- **Key name:** `GOUPC_API_KEY`

### Best Buy API
- **Required for:** Best Buy prices
- **Sign up:** https://developer.bestbuy.com/ → Create an account → Get API key
- **Free tier:** unlimited (rate limited)
- **Key name:** `BESTBUY_API_KEY`

### eBay Browse API
- **Required for:** eBay prices
- **Sign up:** https://developer.ebay.com/ → Create account → My Account → Application Access
  1. Create a new application (Production)
  2. Copy the **App ID (Client ID)** → `EBAY_APP_ID`
  3. Copy the **Cert ID (Client Secret)** → `EBAY_APP_SECRET`
- **Free tier:** generous rate limits for Browse API
- **Key names:** `EBAY_APP_ID`, `EBAY_APP_SECRET`

### SerpAPI (Google Shopping — covers 20+ stores)
- **Required for:** Google Shopping results (Walmart, Target, and many more)
- **Sign up:** https://serpapi.com/ → Create account → Dashboard → API Key
- **Free tier:** 100 searches/month
- **Key name:** `SERPAPI_API_KEY`

### Walmart
- No API key required — uses HTML scraping. May occasionally be blocked by anti-bot measures.

## Running Tests

```bash
# Unit tests (mocked, no API keys needed)
pytest -v

# Integration tests (hits real APIs, requires .env keys)
pytest tests/connectors/test_integration.py -v -s
```

Integration tests auto-skip any connector whose key is missing from `.env`.

## Project Structure

```
shoppingagent/
├── main.py                        # CLI entry point
├── resolver.py                    # UPC → product name (Go-UPC API)
├── models.py                      # Product and PriceResult dataclasses
├── aggregator.py                  # Parallel connector runner
├── formatter.py                   # Rich table + JSON/CSV writer
├── config.py                      # Loads API keys from .env
├── connectors/
│   ├── base.py                    # Abstract BaseConnector
│   ├── bestbuy.py                 # Best Buy API
│   ├── ebay.py                    # eBay Browse API
│   ├── google_shopping.py         # SerpAPI Google Shopping
│   └── walmart.py                 # Walmart HTML scraping
├── tests/
│   ├── connectors/
│   │   ├── test_integration.py    # Live API tests (requires keys)
│   │   ├── test_base.py
│   │   ├── test_bestbuy.py
│   │   ├── test_ebay.py
│   │   ├── test_google_shopping.py
│   │   └── test_walmart.py
│   ├── test_aggregator.py
│   ├── test_config.py
│   ├── test_formatter.py
│   ├── test_main.py
│   ├── test_models.py
│   └── test_resolver.py
├── results/                       # Output files (gitignored)
├── .env                           # Your API keys (gitignored — never commit)
├── .env.example                   # Key names template (safe to commit)
└── requirements.txt
```

## Adding a New Store

1. Create `connectors/newstore.py` implementing `BaseConnector`
2. Add it to `CONNECTORS` list in `main.py`

Nothing else changes — the aggregator, formatter, and CLI handle it automatically.

## Security Notes

- API keys are loaded exclusively from `.env` via `python-dotenv`
- `.env` is gitignored — never committed to version control
- `.env.example` contains only placeholder values — safe to commit
- All dependencies are pinned to latest stable versions in `requirements.txt`
