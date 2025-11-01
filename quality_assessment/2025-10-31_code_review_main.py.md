# Code Review Record — Demo/main.py (BahtBuddy)

- **Date:** 2025-10-31
- **Duration:** 60 minutes
- **Repository:** BahtBuddy
- **Commit/PR:** `<commit SHA or PR #>`
- **File Under Review:** `main.py`

## Participants

- **Author/Committer:** Chirayu “Tuey” Sukhum
- **Reviewer(s):** Khant Phyo Wai (KP), Kris Luangpenthong (Ken)
- **Scribe:** Thanakrit P. (Pass)

## Context (Author)

### Purpose
Core domain layer for BahtBuddy personal finance with double-entry bookkeeping: account initialization (Chart of Accounts), opening balances, transactions (debit/credit), budgets, and basic reporting (budget vs actual).

### Key Contracts
- All functions return `{"ok": True/False, ...}` dicts.
- Double-entry invariant: every transaction debits one account and credits another for the same positive amount.
- Account categories: `asset` | `liability` | `income` | `expense`.

### Known Risks/Hotspots
- Validation relies on an external validation module.
- The database adapter is thinly wrapped; errors bubble up.
- COA init may insert duplicates across multiple runs.

## Automated Signals (before review)

- **Size (approx):** ~260 lines.
- **Cyclomatic complexity:** Low to moderate (most functions short; some branching in loaders and reports).
- **Maintainability:** Good structure, but missing centralized error/log handling; category rules not enforced in transactions.
- *Note: Radon/Lizard reports to be attached separately after CI run.*

## Findings (Issues & Suggestions)

| # | Severity | Location (file:line) | Snippet / Reference | Issue Summary | Rationale | Recommendation | Owner | Status |
|---|---|---|---|---|---|---|---|---|
| 1 | High | `add_transaction` | `if debit_id == credit_id:` | Missing accounting category checks. No guard that debit and credit account types create a valid posting (e.g., expense should be debited, income credited). | Prevents a class of data errors (e.g., crediting an expense). | Fetch both account types and validate against simple rules: (expense ← debit), (income ← credit), (asset/liability debits/credits change sign as expected). Reject invalid combos or allow only defined mappings. | Author | Open |
| 2 | High | `budget_report` | `variance & pct calc` | Division semantics / `None` handling. `pct_of_budget` is `None` when budget is 0; GUI/report code may not handle `None`. | Risk of UI crashes or misrendered cells. | Return numeric `0.0` for `pct_of_budget` when budget is 0 and actual is 0; otherwise consider 'inf' or keep `None` but document and ensure UI formats it. Add tests. | Reviewer KP | Open |
| 3 | High | COA init | `init_coa_default`, `init_coa_from_*` | Duplicate account insertion risk. Re-running init can attempt to reinsert the same account names. | Constraint violations or silent duplicates depending on the DB layer. | Enforce unique `(name,type)` at the DB level; in code, use `INSERT OR IGNORE` (or `ON CONFLICT DO NOTHING`) and report counts (added/skipped). Provide `init_coa_if_empty()` helper. | Author | Open |
| 4 | Medium | `modify_transaction` | passes `**fields` directly | Underspecified field sanitation. No whitelist; mismatched keys or wrong types could reach the DB layer. | Data integrity erosion. | Whitelist keys (`amount`, `date`, `debit_account_id`, `credit_account_id`, `notes`), coerce types, and reject unknown fields. Add schema validation. | Reviewer Ken | Open |
| 5 | Medium | COA constants | `DEFAULT_COA` | Mixed semantics in COA (accounts vs categories). Entries like “Salary”, “Food & Dining” look like categories rather than ledger accounts. | Confusion between chart-of-accounts (postable accounts) vs reporting categories; affects budget/report joins. | Decide model: (A) keep as concrete accounts and introduce a separate categories table; or (B) mark some as categories and support a mapping table `account_categories`. Document clearly. | Team | Open |
| 6 | Medium | `get_balance` | returns raw float | Sign conventions for liabilities/income not defined. UI may display liabilities as negative when conceptually you want a positive “amount owed”. | UX confusion. | Define balance semantics by type (e.g., assets positive = debit balance; liabilities positive = credit balance). Wrap DB result into a normalized presentation balance per type. Document. | Author | Open |
| 7 | Medium | `init_coa_from_*` | file parsers | Input trust and error reporting. CSV/JSON parsers skip invalid rows silently; errors bubble up without line numbers. | Hard to troubleshoot user-provided files. | Accumulate per-row errors with line numbers/keys and return `{"ok": False, "errors":[...]}` on total failure; on partial success, include added and skipped arrays. | Reviewer KP | Open |
| 8 | Medium | `__main__` | `input(...)` | Blocking input prevents headless runs. The executable cannot be run in CI or as a service. | Automation blocker. | Gate behind `if sys.stdout.isatty(): input(...)` or remove; provide a CLI flag `--wait`. | Author | Open |
| 9 | Low | Module | `prints` in `__main__` | Unstructured logging. | Harder to trace in production. | Use the `logging` module with levels; reserve prints for CLI output. | Reviewer Ken | Open |
| 10 | Low | API design | return dicts | Ad-hoc response envelopes. | Inconsistent across modules as the codebase grows. | Define `Result[T] = {"ok": bool, "data"?: T, "error"?: str, ...}` as a `TypedDict` or Pydantic model for stronger contracts. | Team | Open |
| 11 | Low | Validation coupling | external validation | Sparse input messages. | Users get generic errors. | Propagate reasoned messages (e.g., “date must be YYYY-MM-DD”). Add unit tests for boundary cases. | Reviewer KP | Open |
| 12 | Low | Style | missing docstrings | Docs are thin at the function level. | Onboarding cost. | Add docstrings specifying parameters, return shape, and side effects. | Author | Open |

## Inline Notes (embedded code fragments)

### A) Transaction category enforcement (proposed guard)
```python
def add_transaction(date: str, amount: float, debit_id: int, credit_id: int, notes: str = "") -> Dict[str, Any]: 
    if debit_id == credit_id: 
        return {"ok": False, "error": "Debit and credit accounts must differ."} 
    if not (db.account_exists(debit_id) and db.account_exists(credit_id)): 
        return {"ok": False, "error": "One or both accounts do not exist."} 
    if not ymd(date) or not amount_pos(amount): 
        return {"ok": False, "error": "Invalid date or amount."} 
 
    debit_type = db.get_account_type(debit_id)   # returns "asset|liability|income|expense" 
    credit_type = db.get_account_type(credit_id) 
 
    # Simple rule set: expenses should be debited; incomes credited 
    if credit_type == "expense" or debit_type == "income": 
        return {"ok": False, "error": "Invalid posting: expenses should be debited; income should be credited."} 
 
    db.insert_txn(date, float(amount), debit_id, credit_id, notes or "") 
    return {"ok": True}
