"""
main.py

Personal finance management system with double-entry bookkeeping.
Provides functions for managing accounts, transactions, budgets,
and financial reports following double-entry accounting principles.

Created by Chirayu Sukhum (Tuey), October 14, 2025
"""

import csv
import json
from typing import Any, Dict, List, Optional, Tuple

import database as db
from validation import ymd, ym, amount_pos, account_type_valid


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

DEFAULT_TRANSACTION_LIMIT = 200
DEFAULT_TRANSACTION_OFFSET = 0

# Chart of Accounts template for Thai banking/finance context
DEFAULT_COA: List[Tuple[str, str]] = [
    # Assets (cash/banks/e-wallets)
    ("Cash", "asset"),
    ("Bank - KBank", "asset"),
    ("Bank - SCB", "asset"),
    ("Bank - Krungthai (KTB)", "asset"),
    ("Bank - Krungsri (BAY)", "asset"),
    ("Bank - Bangkok Bank (BBL)", "asset"),
    ("Bank - TMBThanachart (TTB)", "asset"),
    ("Bank - UOB Thailand", "asset"),
    ("Bank - CIMB Thai", "asset"),
    ("Bank - KKP", "asset"),
    ("Bank - GSB", "asset"),
    ("Bank - Other", "asset"),
    ("Wallet - TrueMoney", "asset"),
    ("Wallet - Rabbit LINE Pay", "asset"),
    ("Wallet - AirPay", "asset"),
    ("Wallet - PromptPay", "asset"),
    ("Wallet - PayPal", "asset"),
    ("Wallet - Alipay", "asset"),
    ("Wallet - WeChat Pay", "asset"),
    ("Wallet - ShopeePay", "asset"),
    ("Wallet - GrabPay", "asset"),
    ("Wallet - Other", "asset"),
    # Liabilities (credit cards)
    ("Credit Card - KBank", "liability"),
    ("Credit Card - SCB", "liability"),
    ("Credit Card - Krungsri (BAY/FirstChoice)", "liability"),
    ("Credit Card - KTC", "liability"),
    ("Credit Card - BBL", "liability"),
    ("Credit Card - UOB", "liability"),
    ("Credit Card - AEON", "liability"),
    ("Credit Card - Citi", "liability"),
    ("Credit Card - Other", "liability"),
    # Income
    ("Salary", "income"),
    ("Allowance", "income"),
    ("Freelance / Side Income", "income"),
    ("Interest / Dividends", "income"),
    ("Gifts / Other Income", "income"),
    ("Refunds / Reimbursements", "income"),
    ("Sale of Assets", "income"),
    ("Tax Refund", "income"),
    ("Bonuses / Commissions", "income"),
    ("Investment Income", "income"),
    ("Rental Income", "income"),
    ("Royalties", "income"),
    ("Grants / Scholarships", "income"),
    ("Pension / Retirement", "income"),
    ("Insurance Payouts", "income"),
    ("Lottery / Gambling Winnings", "income"),
    ("Crowdfunding / Donations", "income"),
    ("Cashback / Rewards", "income"),
    ("Selling Personal Items", "income"),
    ("Other Miscellaneous Income", "income"),
    # Expenses (common Thai categories)
    ("Food & Dining", "expense"),
    ("Transportation", "expense"),
    ("Rent", "expense"),
    ("Utilities", "expense"),
    ("Groceries", "expense"),
    ("Shopping", "expense"),
    ("Health & Fitness", "expense"),
    ("Entertainment", "expense"),
    ("Travel", "expense"),
]


# -----------------------------------------------------------------------------
# Database Initialization Functions
# -----------------------------------------------------------------------------

def init() -> Dict[str, bool]:
    """
    Initialize the database schema and tables.
    
    Returns:
        Dictionary with 'ok' key indicating success status
    """
    db.init_db()
    return {"ok": True}


def init_coa_default() -> Dict[str, Any]:
    """
    Initialize chart of accounts with default template.
    Uses the predefined DEFAULT_COA list containing common Thai
    banking accounts, wallets, credit cards, and expense categories.
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            added: Number of accounts successfully added (int)
    """
    added = db.bulk_insert_accounts(DEFAULT_COA)
    return {"ok": True, "added": int(added)}


def init_coa_from_file(path: str) -> Dict[str, Any]:
    """
    Initialize chart of accounts from a CSV or JSON file.
    
    Arguments:
        path: File path to CSV or JSON file containing account definitions
              CSV format: name, type (one account per line)
              JSON format: [{"name": "...", "type": "..."}]
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            added: Number of accounts added (int), if successful
            error: Error message (str), if failed
    """
    rows: List[Tuple[str, str]] = []
    
    if path.lower().endswith(".csv"):
        rows = _load_accounts_from_csv(path)
    else:
        rows = _load_accounts_from_json(path)

    if not rows:
        return {"ok": False, "error": "No valid accounts found in file."}
    
    added = db.bulk_insert_accounts(rows)
    return {"ok": True, "added": int(added)}


def _load_accounts_from_csv(path: str) -> List[Tuple[str, str]]:
    """
    Load account definitions from CSV file.
    
    Arguments:
        path: Path to CSV file
    
    Returns:
        List of tuples containing (account_name, account_type)
    """
    rows = []
    
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or len(row) < 2:
                continue
            
            name = row[0]
            account_type = row[1]
            
            if name and account_type_valid(account_type):
                rows.append((name, account_type))
    
    return rows


def _load_accounts_from_json(path: str) -> List[Tuple[str, str]]:
    """
    Load account definitions from JSON file.
    
    Arguments:
        path: Path to JSON file
    
    Returns:
        List of tuples containing (account_name, account_type)
    """
    rows = []
    
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    
    for item in data:
        name = item.get("name")
        account_type = item.get("type")
        
        if name and account_type_valid(account_type):
            rows.append((name, account_type))
    
    return rows


def get_accounts() -> Dict[str, Any]:
    """
    Retrieve all accounts from the database.
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            items: List of account dictionaries with keys:
                   account_id, name, type, status
    """
    rows = db.get_accounts()
    items = [
        {
            "account_id": row[0],
            "name": row[1],
            "type": row[2],
            "status": row[3]
        }
        for row in rows
    ]
    return {"ok": True, "items": items}


# -----------------------------------------------------------------------------
# Opening Balance Functions
# -----------------------------------------------------------------------------

def set_opening_balance(
    account_id: int,
    amount: float,
    date: str
) -> Dict[str, Any]:
    """
    Set or update the opening balance for an account.
    
    Arguments:
        account_id: ID of the account
        amount: Opening balance amount (must be positive)
        date: Date in YYYY-MM-DD format
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            error: Error message (str), if validation fails
    """
    if not db.account_exists(account_id):
        return {"ok": False, "error": "Account does not exist."}
    
    if not ymd(date) or not amount_pos(amount):
        return {"ok": False, "error": "Invalid opening balance input."}
    
    db.upsert_opening_balance(account_id, float(amount), date)
    return {"ok": True}


# -----------------------------------------------------------------------------
# Transaction Functions (Double-Entry Bookkeeping)
# -----------------------------------------------------------------------------

def add_transaction(
    date: str,
    amount: float,
    debit_id: int,
    credit_id: int,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Add a double-entry transaction to the system.
    In double-entry bookkeeping, every transaction affects two accounts:
    one is debited and one is credited.
    
    Arguments:
        date: Transaction date in YYYY-MM-DD format
        amount: Transaction amount (must be positive)
        debit_id: Account ID to debit (receiving account)
        credit_id: Account ID to credit (source account)
        notes: Optional transaction notes or description
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            error: Error message (str), if validation fails
    """
    if debit_id == credit_id:
        return {"ok": False, "error": "Debit and credit accounts must differ."}
    
    if not (db.account_exists(debit_id) and db.account_exists(credit_id)):
        return {"ok": False, "error": "One or both accounts do not exist."}
    
    if not ymd(date) or not amount_pos(amount):
        return {"ok": False, "error": "Invalid date or amount."}

    db.insert_txn(date, float(amount), debit_id, credit_id, notes or "")
    return {"ok": True}


def transfer(
    date: str,
    amount: float,
    src_account_id: int,
    dst_account_id: int,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Transfer money between accounts.
    This is a convenience wrapper that credits the source account
    and debits the destination account.
    
    Arguments:
        date: Transaction date in YYYY-MM-DD format
        amount: Transfer amount (must be positive)
        src_account_id: Source account ID (money leaves from here)
        dst_account_id: Destination account ID (money goes here)
        notes: Optional transaction notes
    
    Returns:
        Dictionary containing success status or error message
    """
    return add_transaction(
        date,
        amount,
        debit_id=dst_account_id,
        credit_id=src_account_id,
        notes=notes
    )


def record(
    date: str,
    amount: float,
    source_id: int,
    destination_id: int,
    notes: str = ""
) -> Dict[str, Any]:
    """
    Generic record function for GUI interface.
    Credits source account, debits destination account.
    This is an alias for the transfer function.
    
    Arguments:
        date: Transaction date in YYYY-MM-DD format
        amount: Transaction amount (must be positive)
        source_id: Source account ID
        destination_id: Destination account ID
        notes: Optional transaction notes
    
    Returns:
        Dictionary containing success status or error message
    """
    return transfer(
        date,
        amount,
        src_account_id=source_id,
        dst_account_id=destination_id,
        notes=notes
    )


def modify_transaction(txn_id: int, **fields: Any) -> Dict[str, Any]:
    """
    Modify an existing transaction.
    Validates all provided fields before updating.
    
    Arguments:
        txn_id: Transaction ID to modify
        **fields: Variable keyword arguments for fields to update.
                  Valid keys: date, amount, debit_account_id,
                  credit_account_id, notes
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            error: Error message (str), if validation fails
    """
    clean: Dict[str, Any] = {}

    # Validate date if provided
    if "date" in fields:
        date_value = fields["date"]
        if (date_value is not None) and (not ymd(date_value)):
            return {"ok": False, "error": "Invalid date."}
        clean["date"] = date_value

    # Validate amount if provided
    if "amount" in fields:
        amount_value = fields["amount"]
        if (amount_value is not None) and (not amount_pos(amount_value)):
            return {"ok": False, "error": "Invalid amount."}
        clean["amount"] = (
            float(amount_value) if amount_value is not None else None
        )

    # Validate account IDs if provided
    for key in ("debit_account_id", "credit_account_id"):
        if key in fields:
            account_value = fields[key]
            if (account_value is not None) and (
                not db.account_exists(int(account_value))
            ):
                return {"ok": False, "error": f"{key} does not exist."}
            clean[key] = (
                int(account_value) if account_value is not None else None
            )

    # Ensure debit and credit accounts differ
    if _accounts_are_same(clean):
        return {"ok": False, "error": "Debit and credit accounts must differ."}

    if "notes" in fields:
        clean["notes"] = fields["notes"]

    db.update_txn(txn_id, **clean)
    return {"ok": True}


def _accounts_are_same(fields: Dict[str, Any]) -> bool:
    """
    Check if debit and credit account IDs are the same.
    
    Arguments:
        fields: Dictionary containing transaction fields
    
    Returns:
        True if both accounts are specified and identical, False otherwise
    """
    debit = fields.get("debit_account_id")
    credit = fields.get("credit_account_id")
    
    return (
        ("debit_account_id" in fields)
        and ("credit_account_id" in fields)
        and (debit is not None)
        and (credit is not None)
        and (debit == credit)
    )


def delete_transaction(txn_id: int) -> Dict[str, bool]:
    """
    Delete a transaction from the system.
    
    Arguments:
        txn_id: Transaction ID to delete
    
    Returns:
        Dictionary with 'ok' key indicating success
    """
    db.delete_txn(txn_id)
    return {"ok": True}


def view_transactions(
    account_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = DEFAULT_TRANSACTION_LIMIT,
    offset: int = DEFAULT_TRANSACTION_OFFSET
) -> Dict[str, Any]:
    """
    View transactions for a specific account with optional filtering.
    
    Arguments:
        account_id: Account ID to view transactions for
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip (for pagination)
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            items: List of transaction dictionaries
    """
    rows = db.list_txns_for_account(
        account_id,
        date_from,
        date_to,
        limit,
        offset
    )
    items = [
        {
            "txn_id": row[0],
            "date": row[1],
            "amount": float(row[2]),
            "debit_account_id": row[3],
            "credit_account_id": row[4],
            "notes": row[5],
        }
        for row in rows
    ]
    return {"ok": True, "items": items}


def search_transactions(
    src_account_id: Optional[int] = None,
    dst_account_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = DEFAULT_TRANSACTION_LIMIT,
    offset: int = DEFAULT_TRANSACTION_OFFSET,
) -> Dict[str, Any]:
    """
    Search transactions with flexible filtering criteria.
    
    Arguments:
        src_account_id: Optional source (credit) account ID filter
        dst_account_id: Optional destination (debit) account ID filter
        date_from: Optional start date filter (YYYY-MM-DD)
        date_to: Optional end date filter (YYYY-MM-DD)
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip (for pagination)
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            items: List of matching transaction dictionaries
    """
    rows = db.search_txns(
        src_account_id,
        dst_account_id,
        date_from,
        date_to,
        limit,
        offset
    )
    items = [
        {
            "txn_id": row[0],
            "date": row[1],
            "amount": float(row[2]),
            "debit_account_id": row[3],
            "credit_account_id": row[4],
            "notes": row[5],
        }
        for row in rows
    ]
    return {"ok": True, "items": items}


def get_balance(
    account_id: int,
    date_to: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculate the balance of an account up to a specified date.
    
    Arguments:
        account_id: Account ID to calculate balance for
        date_to: Optional cutoff date (YYYY-MM-DD).
                 If None, calculates current balance
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            balance: Account balance (float), if successful
            error: Error message (str), if account doesn't exist
    """
    if not db.account_exists(account_id):
        return {"ok": False, "error": "Account does not exist."}
    
    balance = db.account_balance(account_id, date_to)
    return {"ok": True, "balance": float(balance)}


# -----------------------------------------------------------------------------
# Budget Management Functions
# -----------------------------------------------------------------------------

def create_or_update_budget(
    period: str,
    category: str,
    amount: float
) -> Dict[str, Any]:
    """
    Create or update a budget for a specific period and category.
    
    Arguments:
        period: Budget period in YYYY-MM format
        category: Budget category name
        amount: Budget amount (must be positive)
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            error: Error message (str), if validation fails
    """
    if not ym(period):
        return {"ok": False, "error": "Invalid period (YYYY-MM)."}
    
    if not amount_pos(amount):
        return {"ok": False, "error": "Invalid amount."}
    
    db.upsert_budget(period, category, float(amount))
    return {"ok": True}


def get_budget(period: str) -> Dict[str, Any]:
    """
    Retrieve all budgets for a specific period.
    
    Arguments:
        period: Budget period in YYYY-MM format
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            items: List of budget dictionaries with keys:
                   category, amount
    """
    rows = db.get_budgets(period)
    items = [
        {"category": row[0], "amount": float(row[1])}
        for row in rows
    ]
    return {"ok": True, "items": items}


def budget_report(period: str) -> Dict[str, Any]:
    """
    Generate a budget vs actual spending report for a period.
    Compares budgeted amounts with actual expenses and calculates
    variance and percentage of budget used.
    
    Arguments:
        period: Report period in YYYY-MM format
    
    Returns:
        Dictionary containing:
            ok: Success status (bool)
            rows: List of report dictionaries, sorted by variance
                  (overspending first), with keys:
                  category, budget, actual, variance, pct_of_budget
    """
    budgets = dict(db.get_budgets(period))
    actuals = db.actuals_by_category(period)
    
    categories = sorted(set(budgets) | set(actuals))
    rows = []
    
    for category in categories:
        budget_amount = float(budgets.get(category, 0.0))
        actual_amount = float(actuals.get(category, 0.0))
        variance = budget_amount - actual_amount
        
        if budget_amount > 0:
            pct_of_budget = (actual_amount / budget_amount) * 100.0
        else:
            pct_of_budget = None
        
        rows.append({
            "category": category,
            "budget": budget_amount,
            "actual": actual_amount,
            "variance": variance,
            "pct_of_budget": pct_of_budget
        })
    
    # Sort by variance: negative (over-spend) to the top
    rows.sort(key=lambda x: x["variance"])
    
    return {"ok": True, "rows": rows}