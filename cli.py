import os
from typing import Optional
from dotenv import load_dotenv

import typer
import questionary
from rich.console import Console
from rich.table import Table

from bot.client import BinanceFuturesClient
from bot.orders import OrderManager

load_dotenv()

app = typer.Typer(help="Binance Futures Testnet Trading CLI")
console = Console()

def get_client() -> BinanceFuturesClient:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")
    
    if not api_key or not api_secret or "your_api_key_here" in api_key:
        console.print("[red]Error: Binance API keys not found or invalid in .env file![/red]")
        console.print("Please copy .env.example to .env and insert your testnet credentials.")
        raise typer.Exit(code=1)
        
    return BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

def display_result(result: dict):
    if result.get("success"):
        console.print("\n[green]Order Placed Successfully![/green]")
        table = Table(title="Order Details")
        table.add_column("Order ID", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Executed Qty", justify="right")
        table.add_column("Avg Price", justify="right")
        
        table.add_row(
            str(result.get("orderId", "N/A")),
            str(result.get("status", "N/A")),
            str(result.get("executedQty", "0.0")),
            str(result.get("avgPrice", "0.0")),
        )
        console.print(table)
    else:
        console.print(f"\n[red]Order Failed:[/red] {result.get('error')}")

@app.command()
def order(
    symbol: Optional[str] = typer.Option(None, "--symbol", "-s"),
    side: Optional[str] = typer.Option(None, "--side", "-d"),
    order_type: Optional[str] = typer.Option(None, "--type", "-t"),
    quantity: Optional[float] = typer.Option(None, "--quantity", "-q"),
    price: Optional[float] = typer.Option(None, "--price", "-p"),
    stop_price: Optional[float] = typer.Option(None, "--stopPrice", "-sp"),
    interactive: bool = typer.Option(True, "--no-interactive", help="Disable prompts and strictly use passed args")
):
    """
    Submits a new order to Binance Futures Testnet.
    If arguments are missing, an interactive menu will prompt for them (unless --no-interactive is set).
    """
    # Interactive Prompts for missing args
    if interactive:
        if symbol is None:
            symbol = questionary.text("Enter Symbol (e.g. BTCUSDT):").ask()
        if side is None:
            side = questionary.select("Select Side:", choices=["BUY", "SELL"]).ask()
        if order_type is None:
            order_type = questionary.select("Select Order Type:", choices=["MARKET", "LIMIT", "STOP_MARKET"]).ask()
        if quantity is None:
            q_str = questionary.text("Enter Quantity (e.g. 0.001):").ask()
            if q_str:
                quantity = float(q_str)
        if order_type == "LIMIT" and price is None:
            p_str = questionary.text("Enter Limit Price:").ask()
            if p_str:
                price = float(p_str)
        if order_type == "STOP_MARKET" and stop_price is None:
            sp_str = questionary.text("Enter Stop Price:").ask()
            if sp_str:
                stop_price = float(sp_str)
                
    if not all([symbol, side, order_type, quantity]):
        console.print("[red]Missing required arguments. Use --help for usage details.[/red]")
        raise typer.Exit(code=1)

    console.print("\n[blue]Request Summary:[/blue]")
    console.print(f"Symbol: {symbol} | Side: {side} | Type: {order_type} | Qty: {quantity}")
    if price: console.print(f"Price: {price}")
    if stop_price: console.print(f"Stop Price: {stop_price}")
    
    if interactive:
        confirm = questionary.confirm("Proceed with this order?").ask()
        if not confirm:
            console.print("[yellow]Order cancelled.[/yellow]")
            raise typer.Exit()
            
    client = get_client()
    manager = OrderManager(client)
    
    with console.status("[blue]Executing order on Binance Testnet..."):
        result = manager.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price
        )
        
    display_result(result)
    
@app.command()
def test_connection():
    """Verify testnet connectivity via public /fapi/v1/exchangeInfo."""
    try:
        client = get_client()
        with console.status("[blue]Connecting..."):
            res = client.get_exchange_info()
            server_time = res.get('serverTime')
        console.print(f"[green]Connected successfully! Server time: {server_time}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to connect:[/red] {e}")

if __name__ == "__main__":
    app()
