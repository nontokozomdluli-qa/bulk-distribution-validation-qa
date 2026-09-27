# TASK 3 - AI Prompt Log

## Goal
Create Playwright automation for distribution/transaction integrity checks with period-driven execution and clear run documentation.

## Useful prompts used
1. Create Playwright tests for Distributions and Transactions validation using SQLite queries.
2. Implement checks for COMPLETED distributions and APPROVED transactions by period.
3. Add tests to detect completed distributions without approved transactions.
4. Add tests to ensure no completed distribution has REJECTED or PENDING transactions.
5. Add period selection logic with TEST_PERIOD, DISTRIBUTION_PERIOD, and TRANSACTION_PERIOD.
6. Add a default latest-period fallback for both distribution and transaction checks.
7. Create mocked status-check flow tests for invalid client format and missing distribution period.
8. Improve README runbook with PowerShell and Bash examples.

## What AI accelerated
- Initial Playwright test scaffolding and SQL-driven assertions.
- Environment variable period-selection logic.
- Mocked edge-case test scenario drafting.
- Documentation clarity and command examples.

## What was manually validated
- Test runs and period-based execution behavior.
- Review of generated Playwright report and failing scenarios.
- Final regression-priority decisions and scope boundaries.

## Output artifacts
- task 3/tests/distribution-transactions.spec.js
- task 3/tests/status-check-flow.mocked.spec.js
- task 3/playwright.config.js
- task 3/README.md
- task 3/SOLUTION.md
