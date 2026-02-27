import json
import csv
import re
from pathlib import Path
from datetime import date
from rich.console import Console
from rich.table import Table
from models import PriceResult, Product

console = Console()


def display(product: Product, results: list[PriceResult], failed_stores: list[str] | None = None) -> None:
    store_count = len({r.store for r in results})
    console.print(f"\n[bold]Searching for:[/bold] {product.name}")
    console.print(f"[dim]Found {len(results)} results across {store_count} stores[/dim]\n")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Store", min_width=15)
    table.add_column("Price", justify="right", min_width=10)
    table.add_column("Condition", min_width=12)
    table.add_column("Availability", min_width=12)
    table.add_column("URL", no_wrap=False, max_width=55)

    for r in results:
        price_str = f"${r.price:.2f}"
        table.add_row(r.store, price_str, r.condition, r.availability, r.url)

    console.print(table)

    if failed_stores:
        console.print(f"\n[yellow]Stores unreachable: {', '.join(failed_stores)}[/yellow]")


def save(product: Product, results: list[PriceResult]) -> tuple[Path, Path]:
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", product.name.lower()).strip("-")
    today = date.today().isoformat()
    base = results_dir / f"{slug}-{today}"

    json_path = base.with_suffix(".json")
    csv_path = base.with_suffix(".csv")

    data = [
        {
            "store": r.store,
            "price": r.price,
            "currency": r.currency,
            "condition": r.condition,
            "availability": r.availability,
            "url": r.url,
        }
        for r in results
    ]

    json_path.write_text(json.dumps(data, indent=2))

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["store", "price", "currency", "condition", "availability", "url"])
        writer.writeheader()
        writer.writerows(data)

    return json_path, csv_path
