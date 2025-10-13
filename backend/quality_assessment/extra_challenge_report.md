# Extra Challenge: LLM vs Static Analysis

**Static Tool:** Semgrep (auto ruleset)  
**LLM Assistant:** ChatGPT (Code Review)  
**File Reviewed:** models.py  
**Date:** 2025-10-13  

## Comparison
- Semgrep reported 0 issues (clean run).
- The LLM identified deeper design suggestions:
  - Add relationships between tables.
  - Use Date/DateTime instead of String.
  - Use Numeric for precise financial values.
  - Add docstrings and enums for maintainability.

## Determinism
Re-running Semgrep produced identical results, showing deterministic behavior.

## Conclusion
Semgrep validated the absence of rule-based defects, while the LLM added architectural, readability, and data-accuracy improvements—demonstrating that static analysis ensures code safety, whereas LLM reviews enhance design and clarity.
