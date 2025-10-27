# BahtBuddy — UC Functional Test Run (Pages 1–5)
_Generated: 2025-10-27 21:43:29_  
| UC ID | Title | Result | Notes |
|:------|-------|:------:|-------|
| UC-SETUP-01 | Initialize database schema | PASS |  |
| UC-IM-01 | Import COA (valid CSV) | PASS | added=6 |
| UC-IM-02 | Import COA (invalid schema) | PASS | No valid accounts found in file. |
| UC-AC-01 | Get accounts (after import) | PASS | count=6 |
| UC-AC-02 | Set opening balance for Cash | PASS |  |
| UC-TR-01 | Record expense txn | PASS |  |
| UC-TR-02 | Reject negative-amount txn | PASS |  |
| UC-TR-01 | Record income txn | PASS |  |
| UC-TR-03 | Search transactions (Utilities) | PASS |  |
| UC-TR-03 | Modify transaction | PASS |  |
| UC-TR-03 | Delete transaction | PASS |  |
| UC-EX-01 | Export transactions to CSV | PASS | count=1 |
| UC-TR-02 | Lock period 2025-10 | PASS |  |
| UC-TR-02 | Reject edit in locked period | PASS |  |
| UC-TR-02 | Allow reversal in open period | PASS |  |
| UC-BU-01 | Create budget for Groceries | PASS |  |
| UC-BU-01 | Copy budget grid to next month | PASS |  |
| UC-RP-01 | Run Budget vs Actual (2025-10) | PASS | rows=1 |
| UC-RP-01 | Drill-down to Groceries | PASS |  |
| UC-SR-01 | Global search 'Cash' | PASS |  |
| UC-SR-01 | Search nonexistent | PASS |  |
| UC-ST-01 | Toggle dark theme | PASS |  |
| UC-ST-01 | Theme persists | PASS |  |

**Summary:** 23 passed / 23 total