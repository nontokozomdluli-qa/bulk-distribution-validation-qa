# Task 2 SQL Queries

The three requested queries are combined into a single runnable script in [distribution_validation_queries.sql](distribution_validation_queries.sql).

Observed exceptions in the provided SQLite database:
- Missing approved transactions: `C106`, `C109`, `C113`
- Monthly distribution totals: `2026-04`, `2026-05`, `2026-06`
- Amount discrepancies above $0.01: `C103`, `C110`, `C112`
