# BahtBuddy

Personal finance manager with double-entry bookkeeping. Track accounts, record transactions, set monthly budgets, and view budget vs actuals — all stored locally in SQLite with a simple Tkinter GUI.

## Features
- **Accounts**: Assets, liabilities, equity, income, expense accounts with opening balances
- **Transactions**: Add, modify, delete, and search transactions with CSV export
- **Budgets**: Monthly budgets per category with budget vs actual reports
- **GUI**: Dashboard, Accounts, Transactions, and Budgets views
- **Local Storage**: SQLite database file created automatically

## Project Structure
```
BahtBuddy/
├── main/
│   ├── gui.py              # Tkinter application (Dashboard, Accounts, Transactions, Budgets)
│   ├── main.py             # Backend API (accounts, transactions, budgets, reports)
│   ├── database.py         # SQLite schema and data access
│   ├── validation.py       # Input validation helpers
│   └── BahtBuddy.spec      # PyInstaller spec
├── test/
│   └── test_run_cli.py     # Functional test runner (also exports transactions CSV)
└── test_runs/<YYYY-MM-DD>/ # Artifacts from functional test runs
```

Database file: `main/bahtbuddy.db` (auto-created)

## Requirements
- Python 3.10+ (standard library only; tkinter and sqlite3 are included)
- Windows, macOS, or Linux (GUI tested primarily on Windows)

## Quick Start

### 1. Run the GUI Application
```bash
python main/gui.py
```

- On first launch, the database is initialized automatically
- Go to Accounts and click "Load Default Accounts" to seed a Thai-friendly chart of accounts

### 2. Run Backend Only (CLI Output)
```bash
python main/main.py
```

## Using the App

### Accounts
- Add accounts, set opening balances, view current balances
- Account types: Asset, Liability, Equity, Income, Expense

### Transactions
- Record Expense/Income/Transfer transactions using proper debit/credit accounting
- View, modify, and delete existing transactions

### Budgets
- Set monthly budgets for expense categories
- View budget vs actual reports to track spending

### Tips
- Balances follow double-entry bookkeeping: `balance = opening + debits - credits`
- To reset the app, close it and delete `main/bahtbuddy.db` (removes all data)

## Testing

### Functional Test Runner
Runs end-to-end use cases and generates reports:

```bash
python test/test_run_cli.py
```

Artifacts are written to `test_runs/<date>/` including:
- `results.md` - Test results report
- `transactions_export.csv` - Transaction data export

## Deployment

### Windows Executable
Use the provided build script (installs PyInstaller if needed):

```bat
main\deployment_package\build_bahtbuddy.bat
```

**Manual build:**
```bash
# From repository root
python -m pip install pyinstaller
cd main
python -m PyInstaller --onefile --noconsole gui.py --name "BahtBuddy"
```

Executable will be created at: `main/dist/BahtBuddy.exe`

### macOS (.app bundle)
```bash
# From repository root
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip pyinstaller

# Build
cd main
pyinstaller --name "BahtBuddy" --windowed --onedir gui.py
```

App bundle created at: `main/dist/BahtBuddy.app`

**Run the app:**
```bash
open "main/dist/BahtBuddy.app"
```

**If macOS blocks the app (Gatekeeper):**
```bash
xattr -dr com.apple.quarantine "main/dist/BahtBuddy.app"
open "main/dist/BahtBuddy.app"
```

**Create distribution zip:**
```bash
(cd main/dist && zip -r BahtBuddy-mac.zip BahtBuddy.app)
```

### Linux
**Run directly:**
```bash
python3 main/gui.py
```

**Build executable:**
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip pyinstaller

cd main
pyinstaller --name "BahtBuddy" --windowed --onedir gui.py
```

Built app at: `main/dist/BahtBuddy/`

**Run executable:**
```bash
./main/dist/BahtBuddy/BahtBuddy
```

**Single-file binary:**
```bash
pyinstaller --onefile --noconsole gui.py --name "BahtBuddy"
./main/dist/BahtBuddy
```

**Install tkinter (if missing):**
```bash
sudo apt install python3-tk
```

### Deployment Summary
| Platform | Build Command | Launch Command | Output Path |
|----------|---------------|----------------|--------------|
| Windows | `main\deployment_package\build_bahtbuddy.bat` | Runs automatically | `main\dist\BahtBuddy.exe` |
| macOS | `pyinstaller --name "BahtBuddy" --windowed --onedir gui.py` | `open main/dist/BahtBuddy.app` | `main/dist/BahtBuddy.app` |
| Linux | `pyinstaller --name "BahtBuddy" --windowed --onedir gui.py` | `./main/dist/BahtBuddy/BahtBuddy` | `main/dist/BahtBuddy/` |

## Advanced: Importing a Chart of Accounts

Besides the default account set, you can import accounts programmatically:

**CSV format:** `name,type` (types: asset, liability, equity, income, expense)

**JSON format:** Array of objects, each with `name` and `type`

```python
from main import init, init_coa_from_file
init()
init_coa_from_file("/path/to/coa.csv")  # or .json
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No accounts found" in Accounts tab | Click "Load Default Accounts" button |
| GUI doesn't launch on Linux/macOS | Ensure `tkinter` is installed with your Python distribution |
| Build script fails on Windows | Verify Python is on PATH and rerun `main\deployment_package\build_bahtbuddy.bat` from terminal |
| Missing tkinter on Linux | Run `sudo apt install python3-tk` |

## Authors
- **Chirayu Sukhum** (Tuey)
- **Thanakrit Punyasuntontamrong** (Pass)
- **Khant Phyo Wai** (KP)
- Kris Luangpenthong (Ken)

## License
This project is developed as part of SEN-201 Software Engineering Process coursework at CMKL University.
