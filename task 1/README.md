# Task 1 Bulk Distribution Validation

## Setup
- Use Python 3.14+ or the project virtual environment.
- Install dependencies if needed:
  ```bash
  py -m pip install openpyxl
  ```

## What it does
Runs the CSV validation checks and exports an Excel validation report.

## Run
From the `task 1` folder:
```bash
py validate_distribution_comprehensive.py
```

## Inputs
The script reads these files from the parent `resources` folder:
- `source_calculations.csv`
- `distribution_output.csv`

## Output
The Excel report is saved in:
- `task 1/validation_reports`
