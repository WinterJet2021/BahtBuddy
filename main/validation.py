"""
validation.py

Input validation functions for personal finance management system.
Provides lightweight validation for dates, periods, amounts, and account types.

Created by Chirayu Sukhum (Tuey) and Thanakrit Punyasuntontamrong (Pass), October 14, 2025
"""

from typing import Any


# Valid account types for the double-entry bookkeeping system
VALID_ACCOUNT_TYPES = ("asset", "liability", "equity", "income", "expense")


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
    if not isinstance(date, str):
        return False
    
    if len(date) != 10:
        return False
    
    if (date[4] != "-") or (date[7] != "-"):
        return False
    
    return True


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
    if not isinstance(period, str):
        return False
    
    if len(period) != 7:
        return False
    
    if period[4] != "-":
        return False
    
    return True


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
    try:
        return float(value) > 0
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
    return account_type in VALID_ACCOUNT_TYPES