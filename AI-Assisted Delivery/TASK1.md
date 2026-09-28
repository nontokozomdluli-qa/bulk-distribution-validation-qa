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

## Actual prompts

### Core validation requirements
1. **Record count validation**: Compare distribution and source calculations. Source calculations is source of truth.
2. **Missing records**: Identify clients in source but not in distribution (and vice versa). Include ClientID, Client Name, Source Amount, and table where missing.
3. **Duplicate records**: Check duplicates by ClientID, then by ClientID + Client Name + Source Amount. Report which table has duplicates.
4. **Calculation validation**: Expected Net Amount = (Source Amount × Fee) / 100. Identify incorrect calculated amounts. Results: ClientID, Amount, Expected Net Amount, calc_validated_Amount.
5. **Negative source amounts**: Flag negative values that should not lead to distribution. Results: ClientID, Source Amount, and source table.
6. **Zero amounts**: Flag zero distribution/source amounts. Results: ClientID and which table contains the zero.
7. **Rounding discrepancies**: Compare Expected Net Amount vs Distributed Amount. Results: ClientID, Source Amount, Distributed Amount, Difference.

### Implementation refinements
- Console output includes clear check descriptions (e.g., "Check 1: Source Record Count").
- Normalize amounts before calculation; store in `calc_validation_amount` table.
- Add table names to all result logs.
- Excel status field: FAIL or PASS only (red/green fill).
- Single unified Python script runs all validations and exports Excel report.
- Console output includes both CSV files as sources.
- Logging sequence:
  - "Validation Scripts Running"
  - Validation summary after completion
  - "Validation Scripts Ran Successfully, Exporting Results to Excel"
  - "Validation report successfully created and saved in validation_reports folder"

### Excel output format
- Each check sheet includes check name in header row for clarity.
- Executive Summary tab shows status (FAIL/PASS) with conditional formatting.
- Detailed results tab per check with discrepancies only.

### File organization
- All scripts and artifacts moved to task 1 folder.
- All file paths corrected for task 1 location. 
** Looking at the attached files I want to implement the following validations using SQL. 1. Validate record count by comparing distribution output and source calculations. If the numbers are not the same state the difference. Source calculations is our source of truth. 2. Missing record: Check which clients are in the source calculations but not in the distribution vice versa. Result should state the ClientID, Client Name and Source Amount. 3 Duplicate records: Check duplicate record in both tables by first looking at duplicate by ClientID, if found then duplicate by ClientID + Client Name + Source Amount. Output should state which clients are duplicated in each table. In the result include ClientID, Client Name and Source Amount. 4 Calculation Errors: Expected Net Amount is Calculated by taking source amount and multiply by Fee divide by 100. Using this calculation check which expected net distribution amounts are incorrect. In the result state the Client ID, Source Amount, Expected Net Amount, Correct Net Amount. Validate source calculations table. 5 Negative Source Amounts: Negative source amounts will not lead to any distribution and we should not be doing calculations for those.  look for these in the log result. Result should include Client ID and Source Amount (this is in the source caltulation table). 6 Zero Amount to be distributed: Since there won't be any payment for these we want to highlight them and if they need to be excluded from the run they should be excluded. If Distributed amount is 0 then log Client ID (look at distribution table). 7 Rounding off Errors: Compare Expected Net Amount in source calculations and Distributed amount in distribution output to see if there are any discrepancies in the amounts. For Clients where there are discrepencies log the result with Client ID, Expected Net Amount, Distributed Amount, Difference 
** In the console each check should say what is it is checking because for a user seeing Check 1: does not know what to actions, user Check 1: Source Record Count for example. The calcualtion error validation seems to off (doing the manual check there are some values that are not calculated correctly)/ For this check in order to figure out what could be the issue also log the calcutation done by the validator in the console for debugging purposes.
** Some enhancement for better logging: Check 2 also add distributed amount if there. For check 3 the calculation validation is off as it is finding the wrong client and missing all the other client. Relook at how it it doing the logic. The check should look at source_validations.csv. Extract the Source amount, fee and calculate the amount that should be paid to client. When extracting the amounts/values normalise them and do the calculation. Store the info in a table called calc_validation_amount. And them from the same file take the new value and compare them to the expected_net_amount. Log where there are discrepencies. As the script logs and compares compare for client and excel ouput should be the same table with a new columun calc_validation_amount (only log discrepencies). Check 5 and 6 add table name in the results. Remove check 8, 9 and 10 for the purpose of this exercise. Remove all code added to accomodate it. In the excel sheet Executive Summary, in status just write FAIL or PASS only with filling (red and green respectively). Create one script that I can use and it should run validation and then create the excel summary and pivot table
**Confirm that the scripts added to project do the following. SQL. 1. Validate record count by comparing distribution output and source calculations. If the numbers are not the same state the difference. Source calculations is our source of truth. 2. Missing record: Check which clients are in the source calculations but not in the distribution vice versa. Result should state the ClientID, Client Name and Source Amount, Table they are missing in. 3 Duplicate records: Check duplicate record in both tables by first looking at duplicate by ClientID, if found then duplicate by ClientID + Client Name + Source Amount. Output should state which clients are duplicated in each table. In the result include ClientID, Client Name and Source Amount. 4 Calculation Errors: Expected Net Amount is Calculated by taking source amount and multiply by Fee in the source calculations. Using this calculation check which expected net distribution amounts are incorrect. In the result state the Client ID, Amount, Expected Net Amount, calc_validated_ Amount. Only use source calculations table for this validation. 5 Negative Source Amounts: Negative source amounts will not lead to any distribution and we should not be doing calculations for those. log result and show the table where they were found. Result should include Client ID and Source Amount. 6 Zero Amount to be distributed: Since there won't be any payment for these we want to highlight them and if they need to be excluded from the run they should be excluded. If Distributed amount or source amount is 0 then log Client ID (look at both tables). Log should say which table the value was found 7 Rounding off Errors: In the tables source calculations and distribution output compare values in these tables Expected Net Amount and Distributed amount (These amounts should be equal if not flag those record, show client ID, Client, Source Amount, Distributed Amount, Difference)

At the end add a script that output the results in a excel table for reporting and pivot table.

Delete any script of file that does not need to be in the project. Rename the folder to task_1_bulk_distribution_validation
** Check 4 only found one discrepancy but logged 2 more clients incorrectly. Ensure that it only logs correct clients only. Remove console logging for calculation as it will be in the excel sheet. Pivot table should have more infomation it should be as simple as we have taken the detailed output in excel.  allow the user of the report to drill down a bit more for example missing records gives client ID but these records were missing from which table
** Final decision, remove all pivot table logic, excel output is enough. Add these in the console log include both cvs files as source and not just source_calculations.csv. When validation scripts are running echo that Validation Scripts Running. When they are done running Log the summary. When creating the work book Log in the console Validation Scripts Ran Successfully, Exporting Results to Excel. Once the excel book is created and saved echo Validation report successfully created and save in validation_reports folder.
** Looking at my SOLUTION.md I have come up with a plan to scale it up. Check if I am missing anything and format file accordingly. I have also moved The scripts into folder task 1, ensure file paths are corrected and the script attifacts sit in folder task 1. One more enahncement for the excel sheet, the names of check are too long and do not all fit in the sheetname, so fo each solution write the check name on top of the result like in the picture shown
