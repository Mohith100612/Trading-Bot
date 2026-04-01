# Binance Futures Testnet Trading Bot

This is a simplified Python trading bot designed to place `MARKET`, `LIMIT`, and `STOP_MARKET` orders on the **Binance Futures Testnet (USDT-M)**.

It uses direct REST API calls (`httpx`) bypassing heavy wrapper libraries like `python-binance` to demonstrate exactly how the HMAC SHA256 authentication logic works under the hood. It includes a robust CLI built with `Typer` and an interactable fallback shell using `questionary` and `rich`.

## Architecture & Assumptions
*   **Direct REST Client** (`bot/client.py`): Re-implements the standard HMAC parameter signing that Binance requires on authenticated endpoints.
*   **Logging Strategy** (`bot/logger.py`): We avoid flooding `stdout` (which is kept crisp with rich formatters) by utilizing the standard `logging` module with a `RotatingFileHandler`. All low-level API requests, parameters, output payloads, and exceptions are cleanly written to `logs/trading_bot.log`.
*   **Bonus Features Added**:
    *   **Advanced CLI UX**: Fully interactive if arguments remain empty.
    *   **STOP_MARKET**: Third order type supported out-of-the-box.

---

## Setup Steps

### 1. Requirements
Ensure Python 3.9+ is installed globally or in your container instance.

### 2. Install Packages
It is strongly recommended to use a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate       # On MacOS/Linux
.venv\Scripts\activate.ps1      # On Windows PowerShell
```

Install from `pyproject.toml` (equivalent to requirements.txt):
```bash
pip install .
```

### 3. Setup Credentials
Copy the `.env` template file:
```bash
cp .env.example .env
```
Register and acquire keys at the [Binance Futures Testnet](https://testnet.binancefuture.com) dashboard.
Edit `.env` and fill them out.

---

## How to Run Examples

There are two major modes: Interactive Mode, and CLI Headless Configuration.

### 1. Interactive Method (Easiest)
Simply run the CLI without specific arguments to trigger the menu prompt:
```bash
python cli.py order
```
You will be prompted to select your `Side`, `Order Type`, fill in amounts, and confirm before it sends out requests!

### 2. Headless CLI Scripts
Perfect for batch/bash scripting.

**Market Order:**
```bash
python cli.py order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.05 --no-interactive
```

**Limit Order:**
```bash
python cli.py order --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.1 --price 3200.50 --no-interactive
```

**Stop Market Order:**
```bash
python cli.py order --symbol XRPUSDT --side BUY --type STOP_MARKET --quantity 50 --stopPrice 0.82 --no-interactive
```

### 3. Validating the Logs
Every single runtime (successful or failing API error) is saved efficiently:
```bash
cat logs/trading_bot.log
```
