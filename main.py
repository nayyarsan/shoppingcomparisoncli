import asyncio
from typing import Optional
import typer
from rich.console import Console

from resolver import resolve
from aggregator import run_all
from formatter import display, save
from connectors.bestbuy import BestBuyConnector
from connectors.ebay import EbayConnector
from connectors.google_shopping import GoogleShoppingConnector
from connectors.walmart import WalmartConnector

app = typer.Typer(help="Shopping agent: compare prices across US stores.")
console = Console()

CONNECTORS = [
    BestBuyConnector(),
    EbayConnector(),
    GoogleShoppingConnector(),
    WalmartConnector(),
]


@app.command()
def search(
    query: str = typer.Argument(default="", help="Product name to search for"),
    upc: Optional[str] = typer.Option(None, "--upc", "-u", help="UPC or barcode number"),
):
    """Search for a product and compare prices across US stores."""
    if not query and not upc:
        console.print("[red]Error: provide a product name or --upc[/red]")
        raise typer.Exit(1)

    asyncio.run(_search(query, upc))


async def _search(query: str, upc: Optional[str]) -> None:
    with console.status("[bold green]Resolving product..."):
        product = await resolve(query, upc)

    with console.status(f"[bold green]Searching {len(CONNECTORS)} stores in parallel..."):
        results = await run_all(product, CONNECTORS)

    if not results:
        console.print(f"\n[yellow]No results found for '{product.name}'.[/yellow]")
        return

    display(product, results)
    json_path, csv_path = save(product, results)
    if json_path and csv_path:
        console.print(f"\n[green]Saved to {json_path}[/green]")
        console.print(f"[green]Saved to {csv_path}[/green]")


if __name__ == "__main__":
    app()
