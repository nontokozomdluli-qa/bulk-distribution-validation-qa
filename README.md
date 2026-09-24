# bulk-distribution-validation-qa
Bulk financial distribution validation, SQL database investigation, and local automated regression test framework for Senior QA assessment.

Quick start
- Option 1: install the SQLite CLI if your team prefers it
  - Run from the project root:
    sqlite3 bulk_distribution_validation.db ".read validation/distribution_validations.sql"

- Option 2: no extra installation needed (recommended fallback)
  - From the project root:
    python validate_distribution.py
  - In PowerShell:
    .\run_validation.ps1
  - In Command Prompt:
    run_validation.bat
  - On macOS/Linux:
    bash run_validation.sh

This repository includes a Python fallback that uses the built-in sqlite3 module so collaborators do not need to install the standalone SQLite command-line tool.
