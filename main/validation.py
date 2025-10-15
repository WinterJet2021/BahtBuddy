"""
validation.py

Input validation functions for personal finance management system.
Provides lightweight validation for dates, periods, amounts, and account types.

Created by Chirayu Sukhum (Tuey) and Thanakrit Punyasuntontamrong (Pass), October 14, 2025
"""

# To-do import typing from any
import re
from typing import Any  # For type hints


# Valid account types for the double-entry bookkeeping system
# To-do in future: load from config or database
valid_account_types = {
    "asset": ["Cash", "Bank", "Accounts Receivable"],
    "liability": ["Credit Card", "Loan", "Accounts Payable"],
    "equity": ["Owner's Equity", "Retained Earnings"],
    "income": ["Salary", "Sales", "Interest"],
    "expense": ["Rent", "Utilities", "Food", "Transport"],
}


# -----------------------------------------------------------------------------
# Date Validation Functions
# -----------------------------------------------------------------------------

def ymd(date: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD).
    Performs quick sanity check without full date parsing.
    
    Arguments:
        date: Date string to validate
    
    Returns:
        True if format appears valid, False otherwise
    
    Examples:
        ymd("2025-10-14") returns True
        ymd("2025-1-1") returns False (missing leading zeros)
        ymd("25-10-14") returns False (wrong format)
    """
    # To-do in future: consider using datetime for full validation
    pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    return bool(re.match(pattern, date))


def ym(period: str) -> bool:
    """
    Validate period string format (YYYY-MM).
    Used for budget periods and monthly reports.
    
    Arguments:
        period: Period string to validate
    
    Returns:
        True if format appears valid, False otherwise
    
    Examples:
        ym("2025-10") returns True
        ym("2025-1") returns False (missing leading zero)
        ym("10-2025") returns False (wrong order)
    """
    # To-do in future: consider using datetime for full validation
    pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
    return bool(re.match(pattern, period))
    



# -----------------------------------------------------------------------------
# Amount Validation Functions
# -----------------------------------------------------------------------------

def amount_pos(value: Any) -> bool:
    """
    Validate that a value can be converted to a positive number.
    
    Arguments:
        value: Value to validate (any type)
    
    Returns:
        True if value converts to a number greater than zero,
        False otherwise
    
    Examples:
        amount_pos(100.50) returns True
        amount_pos("25.99") returns True
        amount_pos(0) returns False
        amount_pos(-50) returns False
        amount_pos("abc") returns False
    """
    # To-do in future: consider using decimal.Decimal for precision
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False



# -----------------------------------------------------------------------------
# Account Type Validation Functions
# -----------------------------------------------------------------------------

def account_type_valid(account_type: str) -> bool:
    """
    Validate account type against allowed types.
    
    Arguments:
        account_type: Account type string to validate
    
    Returns:
        True if account type is valid, False otherwise
    
    Valid types:
        - asset: Cash, bank accounts, receivables
        - liability: Credit cards, loans, payables
        - equity: Owner's equity, retained earnings
        - income: Salary, sales, interest received
        - expense: Rent, utilities, food, transport
    """
    # To-do in future: load valid types from config or database
    for types in valid_account_types.values():
        if account_type in types:
            return True
        return False
    