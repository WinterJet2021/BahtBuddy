# BahtBuddy

Personal finance manager with double-entry bookkeeping. Track accounts, record transactions, set monthly budgets, and view budget vs actuals — all stored locally in SQLite with a simple Tkinter GUI.

## Features
- Accounts: assets, liabilities, equity, income, expense; opening balances
- Transactions: add, modify, delete, search; CSV export via test runner
- Budgets: per-category monthly budgets; budget vs actual report
- GUI: Dashboard, Accounts, Transactions, Budgets
- Local SQLite database file created automatically

## Project structure
- `main/`
  - `gui.py` — Tkinter application (Dashboard, Accounts, Transactions, Budgets)
  - `main.py` — backend API (accounts, transactions, budgets, reports)
  - `database.py` — SQLite schema and data access
  - `validation.py` — input validation helpers
  - `BahtBuddy.spec` — PyInstaller spec
  - `deployment_package/build_bahtbuddy.bat` — Windows build script
- `test/test_run_cli.py` — functional test runner (also exports transactions CSV)
- `test_runs/<YYYY-MM-DD>/` — artifacts from the functional test run

Database file: `main/bahtbuddy.db` (auto-created).

## Requirements
- Python 3.10+ (standard library only; tkinter and sqlite3 are included)
- Windows, macOS, or Linux (GUI tested primarily on Windows)

## Quick start
1) Run the GUI

```bash path=null start=null
python main/gui.py
```

- On first launch, the database is initialized automatically.
- Go to Accounts and click “Load Default Accounts” to seed a Thai-friendly chart of accounts.

2) Or start the backend only (CLI output)

```bash path=null start=null
python main/main.py
```

## Using the app
- Accounts: add accounts, set opening balances, view balances
- Transactions: record Expense/Income/Transfer using proper debit/credit
- Budgets: set monthly budgets for expense categories and view budget vs actuals

Tips
- Balances follow double-entry: balance = opening + debits − credits
- To reset the app, close it and delete `main/bahtbuddy.db` (this removes all data)

## Functional test runner (optional)
Runs a set of end-to-end use cases and writes a markdown report and CSV export.

```bash path=null start=null
python test/test_run_cli.py
```

Artifacts are written to `test_runs/<date>/` (e.g., `results.md`, `transactions_export.csv`).

## Build a Windows executable (optional)
Use the provided script (installs PyInstaller if needed), builds, and launches the app.

```bat path=null start=null
main\deployment_package\build_bahtbuddy.bat
```

Manual build example

```bash path=null start=null
# from the repository root
python -m pip install pyinstaller
cd main
python -m PyInstaller --onefile --noconsole gui.py --name "BahtBuddy"
```

The executable will be in `main/dist/BahtBuddy.exe`.

## Importing a Chart of Accounts (advanced)
Besides the default set, you can import accounts programmatically:

- CSV format: `name,type` (types: asset, liability, equity, income, expense)
- JSON format: array of objects, each with `name` and `type`

```python path=null start=null
from main import init, init_coa_from_file
init()
init_coa_from_file("/path/to/coa.csv")  # or .json
```

## Troubleshooting
- “No accounts found” in Accounts: click “Load Default Accounts”.
- GUI doesn’t launch on Linux/macOS: ensure `tkinter` is installed with your Python distribution.
- Build script fails: verify Python is on PATH and rerun `main\deployment_package\build_bahtbuddy.bat` from a terminal.

## Authors
- Chirayu Sukhum (Tuey)
- Thanakrit Punyasuntontamrong (Pass)