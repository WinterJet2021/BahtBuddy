"""
test_run_cli.py

BahtBuddy Functional Test Runner — Use Cases (Pages 1–2 Only)

Covers the backend use cases listed on pages 1–2 of the Integration Test Plan.
Generates a Markdown summary and CSV/JSON artifacts for submission.

Covered UCs (Pages 1–2):
- UC-SETUP-01  Initialize database schema
- UC-IM-01     Import Chart of Accounts (valid)
- UC-IM-02     Reject invalid Chart of Accounts file
- UC-AC-01     Retrieve accounts after import
- UC-AC-02     Set opening balance
- UC-TR-01     Record transactions (expense, income)
- UC-TR-02     Reject invalid transactions (negative amount)
- UC-TR-03     Search / modify / delete transactions
- UC-EX-01     Export transactions to CSV

Not Covered (Pages 3–5):
- GUI flows, period locking/reversal, large/performance COA import, theming, accessibility, etc.
See TEAM TODO at the bottom.

Created by Chirayu Sukhum (Tuey) and Thanakrit Punyasuntontamrong (Pass), October 27, 2025
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Sequence


# -----------------------------------------------------------------------------
# Import Path Setup (so `import main` resolves to ./main/main.py)
# -----------------------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parent.parent            # .../BahtBuddy
MAIN_DIR = REPO_ROOT / "main"                  # .../BahtBuddy/main
if str(MAIN_DIR) not in sys.path:
    sys.path.append(str(MAIN_DIR))

import main  # noqa: E402  (import after path fix)


# -----------------------------------------------------------------------------
# Constants / Paths
# -----------------------------------------------------------------------------
RUN_DIR = (REPO_ROOT / "test_runs" / "2025-10-27").resolve()
DATA_DIR = RUN_DIR / "data"
EVIDENCE_DIR = RUN_DIR / "evidence"

TXN_EXPORT_CSV = RUN_DIR / "transactions_export.csv"
ACCOUNTS_JSON = EVIDENCE_DIR / "accounts_after_import.json"


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def ensure_dirs() -> None:
    """Create output directories if they do not exist."""
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_seed_files() -> None:
    """
    Create minimal seed files for COA import tests if missing.
    These cover only the scope required by Pages 1–2.
    """
    valid = DATA_DIR / "coa_valid.csv"
    invalid = DATA_DIR / "coa_invalid.csv"

    if not valid.exists():
        valid.write_text(
            "name,type\n"
            "Cash,asset\n"
            "Bank - KBank,asset\n"
            "Credit Card - KBank,liability\n"
            "Utilities,expense\n"
            "Groceries,expense\n"
            "Salary,income\n",
            encoding="utf-8",
        )

    if not invalid.exists():
        invalid.write_text(
            "name\n"
            "Cash\n"
            "Salary\n",
            encoding="utf-8",
        )


def write_csv(path: Path, rows: Iterable[Sequence], header: Sequence[str] | None) -> None:
    """Write data to CSV with optional header."""
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header:
            w.writerow(header)
        w.writerows(rows)


# -----------------------------------------------------------------------------
# Results Recording (Use Case oriented)
# -----------------------------------------------------------------------------
RESULTS: List[dict] = []


def rec(uc_id: str, title: str, ok: bool, note: str = "") -> None:
    """Append a single UC result."""
    RESULTS.append({"uc": uc_id, "title": title, "ok": bool(ok), "note": note})


# -----------------------------------------------------------------------------
# Use Cases — Pages 1–2 Only
# -----------------------------------------------------------------------------
def uc_setup_init_schema() -> None:
    """UC-SETUP-01: Initialize database schema."""
    r = main.init()
    rec("UC-SETUP-01", "Initialize database schema", r.get("ok", False))


def uc_import_valid_coa() -> None:
    """UC-IM-01: Import valid Chart of Accounts CSV."""
    r = main.init_coa_from_file(str(DATA_DIR / "coa_valid.csv"))
    ok = r.get("ok", False) and r.get("added", 0) >= 5
    rec("UC-IM-01", "Import COA (valid CSV)", ok, f"added={r.get('added')}")


def uc_import_invalid_coa() -> None:
    """UC-IM-02: Reject invalid COA file."""
    r = main.init_coa_from_file(str(DATA_DIR / "coa_invalid.csv"))
    rec("UC-IM-02", "Import COA (invalid schema)", not r.get("ok", True), r.get("error", ""))


def uc_accounts_list() -> None:
    """UC-AC-01: Retrieve accounts after import."""
    items = main.get_accounts()["items"]
    rec("UC-AC-01", "Get accounts (after import)", len(items) >= 5, f"count={len(items)}")
    ACCOUNTS_JSON.write_text(json.dumps(items, indent=2), encoding="utf-8")


def uc_accounts_opening_balance() -> None:
    """UC-AC-02: Set opening balance for Cash."""
    items = main.get_accounts()["items"]
    name_to_id = {a["name"]: a["account_id"] for a in items}
    cash_id = name_to_id.get("Cash")
    r = main.set_opening_balance(cash_id, 10_000, datetime.now().strftime("%Y-%m-%d"))
    rec("UC-AC-02", "Set opening balance for Cash", r.get("ok", False))


def uc_txn_core_flow() -> None:
    """
    UC-TR-01 / UC-TR-02 / UC-TR-03:
    - UC-TR-01: Record transactions (expense, income)
    - UC-TR-02: Reject invalid transactions (negative amount)
    - UC-TR-03: Search, modify, and delete a transaction
    """
    items = main.get_accounts()["items"]
    name_to_id = {a["name"]: a["account_id"] for a in items}
    cash = name_to_id["Cash"]
    util = name_to_id["Utilities"]
    salary = name_to_id["Salary"]

    # UC-TR-01: Add expense (Utilities from Cash)
    r1 = main.add_transaction(datetime.now().strftime("%Y-%m-%d"), 150, debit_id=util, credit_id=cash, notes="Electric bill")
    rec("UC-TR-01", "Record expense txn (Utilities 150 from Cash)", r1.get("ok", False))

    # UC-TR-02: Reject negative amount
    r2 = main.add_transaction(datetime.now().strftime("%Y-%m-%d"), -10, debit_id=util, credit_id=cash, notes="NEG")
    rec("UC-TR-02", "Reject negative-amount txn", not r2.get("ok", True))

    # UC-TR-01: Add income (Salary to Cash)
    r3 = main.add_transaction(datetime.now().strftime("%Y-%m-%d"), 5000, debit_id=cash, credit_id=salary, notes="Monthly salary")
    rec("UC-TR-01", "Record income txn (Salary 5000 to Cash)", r3.get("ok", False))

    # UC-TR-03: Search + modify + delete (Utilities)
    srch = main.search_transactions(dst_account_id=util)
    have_util = srch.get("ok", False) and len(srch.get("items", [])) >= 1
    rec("UC-TR-03", "Search transactions by destination (Utilities)", have_util, f"count={len(srch.get('items', []))}")
    if have_util:
        t = srch["items"][0]
        m = main.modify_transaction(t["txn_id"], amount=200.0)
        rec("UC-TR-03", "Modify transaction amount to 200", m.get("ok", False))
        d = main.delete_transaction(t["txn_id"])
        rec("UC-TR-03", "Delete transaction", d.get("ok", False))


def uc_export_transactions() -> None:
    """UC-EX-01: Export transactions to CSV."""
    all_txn = main.search_transactions()
    ok = all_txn.get("ok", False)
    items = all_txn.get("items", [])
    rec("UC-EX-01", "Export transactions to CSV", ok, f"count={len(items)}")
    header = ["txn_id", "date", "debit_account_id", "credit_account_id", "amount", "notes"]
    rows = [[t["txn_id"], t["date"], t["debit_account_id"], t["credit_account_id"], t["amount"], t["notes"]] for t in items]
    write_csv(TXN_EXPORT_CSV, rows, header)


# -----------------------------------------------------------------------------
# TEAM TODO — Remaining Use Cases (Pages 3–5)
# -----------------------------------------------------------------------------
# def uc_budget_and_report() -> None:
#     """UC-BU-01 / UC-RP-01: Budgets and Budget vs Actual report."""
#     pass
#
# def uc_gui_validation() -> None:
#     """UC-UI-01..: GUI validation behaviors and error messaging."""
#     pass
#
# def uc_period_locking_and_reversal() -> None:
#     """UC-TR-LOCK-*, UC-TR-REV-*: Locked accounting periods and reversals."""
#     pass
#
# def uc_large_coa_import() -> None:
#     """UC-IM-XX: Performance test for very large COA files."""
#     pass


# -----------------------------------------------------------------------------
# Reporting
# -----------------------------------------------------------------------------
def write_results_md() -> None:
    """Write a Markdown summary table for submission."""
    passed = sum(1 for r in RESULTS if r["ok"])
    failed = sum(1 for r in RESULTS if not r["ok"])

    lines = []
    lines.append("# BahtBuddy — UC Functional Test Run (Pages 1–2)")
    lines.append(f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_  ")
    lines.append("Environment: Local (Python + SQLite)  ")
    lines.append("")
    lines.append("| UC ID | Title | Result | Notes |")
    lines.append("|-----:|-------|:------:|-------|")
    for r in RESULTS:
        status = "PASS" if r["ok"] else "FAIL"
        lines.append(f"| {r['uc']} | {r['title']} | {status} | {r['note']} |")
    lines.append("")
    lines.append(f"**Summary** — Passed: {passed} • Failed: {failed}")
    lines.append("")
    lines.append("> Remaining UCs (Pages 3–5) are left for teammates in this file.")
    (RUN_DIR / "results.md").write_text("\n".join(lines), encoding="utf-8")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main_run() -> None:
    """Execute Page 1–2 use cases in logical order and write results."""
    ensure_dirs()
    ensure_seed_files()

    uc_setup_init_schema()
    uc_import_valid_coa()
    uc_import_invalid_coa()
    uc_accounts_list()
    uc_accounts_opening_balance()
    uc_txn_core_flow()
    uc_export_transactions()

    write_results_md()


if __name__ == "__main__":
    main_run()
