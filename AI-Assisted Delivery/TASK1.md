# TASK 1 - AI Prompt Log

## Goal
Build a reusable Python validation flow for source and distribution CSV outputs with report-friendly discrepancy summaries.

## Useful prompts used
1. Read task requirements and break Task 1 into checkable validation rules with expected outputs.
2. Generate Python checks for source count vs distribution count, missing records, and duplicate records.
3. Add calculation validation between expected net amount and distributed amount with variance details.
4. Add data quality checks for negative source amounts and zero distribution amounts.
5. Refactor the checks into reusable functions and make it easy to toggle checks on or off.
6. Propose an Excel reporting structure for discrepancy output and analyst review.
7. Review this logic and suggest edge cases likely to fail in production.

## What AI accelerated
- First-draft validation logic for all required check categories.
- Structure for reusable checks and readable outputs.
- Documentation wording for setup and run steps.

## What was manually validated
- Script execution against resources/source_calculations.csv and resources/distribution_output.csv.
- Discrepancy counts confirmed before final write-up.
- Business interpretation and production scaling recommendations.

## Output artifacts
- task 1/validate_distribution_comprehensive.py
- task 1/README.md
- task 1/SOLUTION.md
- task 1/validation_reports/
