"""
database.py

Database layer for personal finance management system.
Provides SQLite database operations for accounts, transactions,
budgets, and reports using double-entry bookkeeping principles.

Created by Thanakrit Punyasuntontamrong (Pass), October 14, 2025
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

# Database file path
DB_PATH = Path(__file__).parent / "bahtbuddy.db"


# -----------------------------------------------------------------------------
# Database Connection Management
# -----------------------------------------------------------------------------

@contextmanager
def connect():
    """
    Create a context-managed SQLite database connection.
    Automatically enables foreign key constraints and handles
    commit/close operations.
    
    Yields:
        sqlite3.Connection: Database connection with FK enabled
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    finally:
        conn.close()


# -----------------------------------------------------------------------------
# Database Initialization
# -----------------------------------------------------------------------------

def init_db() -> None:
    """
    Initialize database schema.
    Creates all necessary tables and indexes if they don't exist.
    Tables include: accounts, opening_balances, transactions,
    budgets, reports, and meta.
    """
    ddl = """
    CREATE TABLE IF NOT EXISTS accounts(
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL UNIQUE,
        type       TEXT NOT NULL CHECK (type IN ('asset','liability','equity','income','expense')),
        status     TEXT NOT NULL DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS opening_balances(
        balance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        account_id INTEGER NOT NULL REFERENCES accounts(account_id) ON DELETE CASCADE,
        amount     NUMERIC NOT NULL,
        date       TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS transactions(
        txn_id            INTEGER PRIMARY KEY AUTOINCREMENT,
        date              TEXT NOT NULL,
        amount            NUMERIC NOT NULL CHECK (amount > 0),
        debit_account_id  INTEGER NOT NULL REFERENCES accounts(account_id),
        credit_account_id INTEGER NOT NULL REFERENCES accounts(account_id),
        notes             TEXT
    );

    CREATE TABLE IF NOT EXISTS budgets(
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category  TEXT NOT NULL,
        amount    NUMERIC NOT NULL,
        period    TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS reports(
        report_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        created_at TEXT NOT NULL,
        type       TEXT NOT NULL,
        content    TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS meta(
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    INSERT OR IGNORE INTO meta(key,value) VALUES ('schema_version','1');

    CREATE INDEX IF NOT EXISTS idx_txn_date   ON transactions(date);
    CREATE INDEX IF NOT EXISTS idx_txn_debit  ON transactions(debit_account_id);
    CREATE INDEX IF NOT EXISTS idx_txn_credit ON transactions(credit_account_id);
    CREATE UNIQUE INDEX IF NOT EXISTS idx_budget_period_cat ON budgets(period, category);
    """
    with connect() as conn:
        conn.executescript(ddl)


# -----------------------------------------------------------------------------
# Account Management Functions
# -----------------------------------------------------------------------------

def insert_account(
    name: str,
    account_type: str,
    status: str = "active"
) -> None:
    """
    Insert a new account into the database.
    
    Arguments:
        name: Account name (will be trimmed of whitespace)
        account_type: Account type (asset, liability, equity, income, expense)
        status: Account status (default: 'active')
    """
    with connect() as conn:
        conn.execute(
            "INSERT INTO accounts(name,type,status) VALUES (?,?,?)",
            (name.strip(), account_type.strip(), status.strip()),
        )


def bulk_insert_accounts(rows: Iterable[Tuple[str, str]]) -> int:
    """
    Insert multiple accounts in a single transaction.
    Ignores duplicate account names.
    
    Arguments:
        rows: Iterable of tuples containing (name, type)
    
    Returns:
        Number of accounts successfully inserted
    """
    cleaned_rows = [
        (name.strip(), account_type.strip(), "active")
        for name, account_type in rows
    ]
    
    with connect() as conn:
        cursor = conn.executemany(
            "INSERT OR IGNORE INTO accounts(name,type,status) VALUES (?,?,?)",
            cleaned_rows,
        )
        return cursor.rowcount or 0


def get_accounts() -> List[Tuple[int, str, str, str]]:
    """
    Retrieve all active accounts ordered by name.
    
    Returns:
        List of tuples containing (account_id, name, type, status)
    """
    with connect() as conn:
        return conn.execute(
            """SELECT account_id, name, type, status 
               FROM accounts 
               WHERE status='active' 
               ORDER BY name"""
        ).fetchall()


def get_accounts_by_type(account_type: str) -> List[Tuple[int, str]]:
    """
    Retrieve all active accounts of a specific type.
    
    Arguments:
        account_type: Type of accounts to retrieve
    
    Returns:
        List of tuples containing (account_id, name)
    """
    with connect() as conn:
        return conn.execute(
            """SELECT account_id, name 
               FROM accounts 
               WHERE status='active' AND type=? 
               ORDER BY name""",
            (account_type,),
        ).fetchall()


def get_account_by_name(name: str) -> Optional[Tuple[int, str, str, str]]:
    """
    Retrieve an account by its name.
    
    Arguments:
        name: Account name to search for
    
    Returns:
        Tuple of (account_id, name, type, status) if found, None otherwise
    """
    with connect() as conn:
        return conn.execute(
            "SELECT account_id, name, type, status FROM accounts WHERE name=?",
            (name,),
        ).fetchone()


def get_account_type(account_id: int) -> Optional[str]:
    """
    Get the type of a specific account.
    
    Arguments:
        account_id: ID of the account
    
    Returns:
        Account type string if found, None otherwise
    """
    with connect() as conn:
        row = conn.execute(
            "SELECT type FROM accounts WHERE account_id=?",
            (account_id,),
        ).fetchone()
    return row[0] if row else None


def account_exists(account_id: int) -> bool:
    """
    Check if an account exists in the database.
    
    Arguments:
        account_id: ID of the account to check
    
    Returns:
        True if account exists, False otherwise
    """
    with connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM accounts WHERE account_id=?",
            (account_id,)
        ).fetchone()
    return bool(row)


# -----------------------------------------------------------------------------
# Opening Balance Functions
# -----------------------------------------------------------------------------

def upsert_opening_balance(
    account_id: int,
    amount: float,
    date: str
) -> None:
    """
    Insert an opening balance for an account.
    
    Arguments:
        account_id: ID of the account
        amount: Opening balance amount
        date: Date of the opening balance (YYYY-MM-DD)
    """
    with connect() as conn:
        conn.execute(
            "INSERT INTO opening_balances(account_id, amount, date) VALUES (?,?,?)",
            (account_id, amount, date),
        )


def account_opening_balance(account_id: int) -> float:
    """
    Calculate total opening balance for an account.
    
    Arguments:
        account_id: ID of the account
    
    Returns:
        Sum of all opening balances for the account
    """
    with connect() as conn:
        cursor = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM opening_balances WHERE account_id=?",
            (account_id,),
        )
        return float(cursor.fetchone()[0] or 0.0)


# -----------------------------------------------------------------------------
# Transaction Functions (Double-Entry Bookkeeping)
# -----------------------------------------------------------------------------

def insert_txn(
    date: str,
    amount: float,
    debit_account_id: int,
    credit_account_id: int,
    notes: str
) -> None:
    """
    Insert a new double-entry transaction.
    
    Arguments:
        date: Transaction date (YYYY-MM-DD)
        amount: Transaction amount (must be positive)
        debit_account_id: Account to debit
        credit_account_id: Account to credit
        notes: Transaction notes or description
    """
    with connect() as conn:
        conn.execute(
            """INSERT INTO transactions(date,amount,debit_account_id,credit_account_id,notes)
               VALUES (?,?,?,?,?)""",
            (date, amount, debit_account_id, credit_account_id, notes),
        )


def update_txn(
    txn_id: int,
    *,
    date: Optional[str] = None,
    amount: Optional[float] = None,
    debit_account_id: Optional[int] = None,
    credit_account_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> None:
    """
    Update specific fields of an existing transaction.
    Only provided fields will be updated.
    
    Arguments:
        txn_id: Transaction ID to update
        date: New transaction date (optional)
        amount: New transaction amount (optional)
        debit_account_id: New debit account ID (optional)
        credit_account_id: New credit account ID (optional)
        notes: New transaction notes (optional)
    """
    fields = []
    values = []
    
    field_mapping = {
        "date": date,
        "amount": amount,
        "debit_account_id": debit_account_id,
        "credit_account_id": credit_account_id,
        "notes": notes,
    }
    
    for field_name, field_value in field_mapping.items():
        if field_value is not None:
            fields.append(f"{field_name}=?")
            values.append(field_value)
    
    if not fields:
        return
    
    values.append(txn_id)
    
    with connect() as conn:
        query = f"UPDATE transactions SET {', '.join(fields)} WHERE txn_id=?"
        conn.execute(query, values)


def delete_txn(txn_id: int) -> None:
    """
    Delete a transaction from the database.
    
    Arguments:
        txn_id: Transaction ID to delete
    """
    with connect() as conn:
        conn.execute("DELETE FROM transactions WHERE txn_id=?", (txn_id,))


def get_txn(txn_id: int) -> Optional[Tuple]:
    """
    Retrieve a specific transaction by ID.
    
    Arguments:
        txn_id: Transaction ID to retrieve
    
    Returns:
        Tuple of (txn_id, date, amount, debit_account_id, 
        credit_account_id, notes) if found, None otherwise
    """
    with connect() as conn:
        return conn.execute(
            """SELECT txn_id,date,amount,debit_account_id,credit_account_id,notes
               FROM transactions WHERE txn_id=?""",
            (txn_id,),
        ).fetchone()


def list_txns_for_account(
    account_id: int,
    date_from: Optional[str],
    date_to: Optional[str],
    limit: int = 200,
    offset: int = 0,
) -> List[Tuple]:
    """
    List transactions for a specific account with optional date filtering.
    Returns transactions where the account is either debited or credited.
    
    Arguments:
        account_id: Account ID to filter transactions
        date_from: Start date filter (YYYY-MM-DD), None for no start limit
        date_to: End date filter (YYYY-MM-DD), None for no end limit
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip (for pagination)
    
    Returns:
        List of transaction tuples ordered by date (newest first)
    """
    query_parts = [
        "SELECT txn_id,date,amount,debit_account_id,credit_account_id,notes",
        "FROM transactions WHERE (debit_account_id=? OR credit_account_id=?)",
    ]
    params: List = [account_id, account_id]
    
    if date_from:
        query_parts.append("AND date>=?")
        params.append(date_from)
    
    if date_to:
        query_parts.append("AND date<=?")
        params.append(date_to)
    
    query_parts.append("ORDER BY date DESC, txn_id DESC LIMIT ? OFFSET ?")
    params += [limit, offset]
    
    with connect() as conn:
        return conn.execute(" ".join(query_parts), params).fetchall()


def search_txns(
    src_account_id: Optional[int] = None,
    dst_account_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
) -> List[Tuple]:
    """
    Search transactions with flexible filtering criteria.
    
    Arguments:
        src_account_id: Source (credit) account ID filter
        dst_account_id: Destination (debit) account ID filter
        date_from: Start date filter (YYYY-MM-DD)
        date_to: End date filter (YYYY-MM-DD)
        limit: Maximum number of transactions to return
        offset: Number of transactions to skip (for pagination)
    
    Returns:
        List of matching transaction tuples ordered by date (newest first)
    """
    query_parts = [
        """SELECT txn_id,date,amount,debit_account_id,credit_account_id,notes 
           FROM transactions WHERE 1=1"""
    ]
    params: List = []
    
    if src_account_id is not None:
        query_parts.append("AND credit_account_id=?")
        params.append(src_account_id)
    
    if dst_account_id is not None:
        query_parts.append("AND debit_account_id=?")
        params.append(dst_account_id)
    
    if date_from:
        query_parts.append("AND date>=?")
        params.append(date_from)
    
    if date_to:
        query_parts.append("AND date<=?")
        params.append(date_to)
    
    query_parts.append("ORDER BY date DESC, txn_id DESC LIMIT ? OFFSET ?")
    params += [limit, offset]
    
    with connect() as conn:
        return conn.execute(" ".join(query_parts), params).fetchall()


# -----------------------------------------------------------------------------
# Account Balance Calculation Functions
# -----------------------------------------------------------------------------

def account_period_sums(
    account_id: int,
    date_to: Optional[str] = None
) -> Tuple[float, float]:
    """
    Calculate sum of debits and credits for an account.
    
    Arguments:
        account_id: Account ID to calculate sums for
        date_to: Optional cutoff date (YYYY-MM-DD), 
                 None for all transactions
    
    Returns:
        Tuple of (sum_debits, sum_credits)
    """
    query_debit = (
        "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE debit_account_id=?"
    )
    query_credit = (
        "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE credit_account_id=?"
    )
    params_debit = [account_id]
    params_credit = [account_id]
    
    if date_to:
        query_debit += " AND date<=?"
        query_credit += " AND date<=?"
        params_debit.append(date_to)
        params_credit.append(date_to)
    
    with connect() as conn:
        sum_debits = float(
            conn.execute(query_debit, params_debit).fetchone()[0] or 0.0
        )
        sum_credits = float(
            conn.execute(query_credit, params_credit).fetchone()[0] or 0.0
        )
    
    return sum_debits, sum_credits


def account_balance(
    account_id: int,
    date_to: Optional[str] = None
) -> float:
    """
    Calculate account balance using double-entry formula.
    Balance = opening_balance + debits - credits
    
    Arguments:
        account_id: Account ID to calculate balance for
        date_to: Optional cutoff date (YYYY-MM-DD),
                 None for current balance
    
    Returns:
        Account balance as of the specified date
    """
    opening_balance = account_opening_balance(account_id)
    sum_debits, sum_credits = account_period_sums(account_id, date_to)
    return opening_balance + sum_debits - sum_credits


# -----------------------------------------------------------------------------
# Budget Management Functions
# -----------------------------------------------------------------------------

def upsert_budget(period: str, category: str, amount: float) -> None:
    """
    Create or update a budget for a specific period and category.
    Uses SQLite's UPSERT functionality to handle duplicates.
    
    Arguments:
        period: Budget period (YYYY-MM)
        category: Budget category (should match expense account name)
        amount: Budget amount
    """
    with connect() as conn:
        conn.execute(
            """INSERT INTO budgets(period, category, amount) VALUES (?,?,?)
               ON CONFLICT(period, category) DO UPDATE SET amount=excluded.amount""",
            (period, category, amount),
        )


def get_budgets(period: str) -> List[Tuple[str, float]]:
    """
    Retrieve all budgets for a specific period.
    
    Arguments:
        period: Budget period (YYYY-MM)
    
    Returns:
        List of tuples containing (category, amount) ordered by category
    """
    with connect() as conn:
        return conn.execute(
            "SELECT category, amount FROM budgets WHERE period=? ORDER BY category",
            (period,),
        ).fetchall()


def actuals_by_category(period: str) -> Dict[str, float]:
    """
    Calculate actual expenses by category for a specific period.
    Sums all debit transactions for expense accounts within the period.
    
    Arguments:
        period: Period to calculate actuals for (YYYY-MM)
    
    Returns:
        Dictionary mapping category names to actual expense amounts
    """
    with connect() as conn:
        rows = conn.execute(
            """SELECT a.name AS category, COALESCE(SUM(t.amount), 0) AS actual
               FROM accounts a
               LEFT JOIN transactions t
                 ON a.account_id = t.debit_account_id
                AND substr(t.date,1,7) = ?
               WHERE a.type = 'expense'
               GROUP BY a.name""",
            (period,),
        ).fetchall()
    
    return {row[0]: float(row[1] or 0.0) for row in rows}