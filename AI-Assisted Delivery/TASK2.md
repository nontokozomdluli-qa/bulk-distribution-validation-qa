# TASK 2 - AI Prompt Log

## Goal
Produce SQL validations for distribution and transaction integrity, then document root-cause analysis for the failure scenario.

## Useful prompts used
1. Write SQLite queries to find clients with completed distributions but no approved transactions.
2. Write a monthly distribution totals query grouped by period.
3. Write a discrepancy query where source amount and distributed amount differ above a tolerance.
4. Refactor SQL for readability and SQLite compatibility.
5. Convert incident notes into a concise root-cause analysis with severity, reproduction, impact, and remediation.
6. Review RCA language for clarity and business risk communication.

## What AI accelerated
- Fast first-draft SQL for all required checks.
- Query refinement and result summarization structure.
- RCA report structure and concise wording.

## What was manually validated
- SQL outputs were reviewed against expected exception patterns.
- RCA narrative was cross-checked with provided error log evidence.
- Final remediation priorities were chosen manually.

## Output artifacts
- task 2/distribution_validation_queries.sql
- task 2/RootCauseAnalysis.md
- task 2/SOLUTION.md
