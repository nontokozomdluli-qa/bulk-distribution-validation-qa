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

## Actual prompts

### SQL query requirements
1. **Missing approved transactions**: Identify clients in distribution output but with no corresponding approved transaction record.
2. **Monthly distribution totals**: Calculate total distributed amount per month for the period covered by the data.
3. **Amount discrepancies**: Identify clients whose distributed amount differs from calculated source amount by more than $0.01.

### SQL implementation
- Combine all three queries into a single runnable script.
- Ensure SQLite compatibility and readable output.

### Root-cause analysis requirements
Review incident context and log extract:
- Date: 2026-06-14 02:14 UTC
- Issue: ArithmeticException (division by zero) in FeeCalculator
- Client affected: C0453
- Root cause: fee_pct = NULL
- Batch status: 4,811 succeeded, 1 failed

### RCA structure and content
- **Severity**: High (client missed entire distribution)
- **Component**: Fee Calculator
- **Description**: Pipeline failed due to NULL fee_pct attempting division by zero
- **Reproduction steps**: Set fee_pct to NULL for a client and trigger distribution run
- **Supporting evidence**: Include specific log line references and stack trace
- **Business impact**: 
  - Financial: Client did not receive distribution
  - Reputational: Risk of negative attention if client discovers missed payment
  - Operational: Additional work for downstream teams, SLA delays, batch continuation despite failure
  - Logging gap: Final log message "1 record failed, 4,811 succeeded" masks severity
- **Proposed resolution**:
  - Enforce data schema constraints (NOT NULL on fee_pct)
  - Add NULL value default handling (fee_pct = 0.00)
  - Update error handling to fail fast on critical errors, not silently skip

### Document format
- Clear structure for developer reference and business stakeholder review
- Evidence-based conclusions with log line citations
- Actionable remediation priorities
** Looking at the different tables in the distribution_qa(1) write the following SQL queries. ● Identify clients that appear in the distribution output but have no corresponding approved transaction record.
● Calculate the total distributed amount per month for the period covered by the data.
● Identify any clients whose distributed amount differs from their calculated source amount by more than $0.01.
** turn these into a single query script
** This my root cause analysis review and give feedback 
```
"[Bug] BatchdistributionJob 2026-06-14 Run Interrupted due to arithmetic exception: divided by zero where client had NULL fee percentage

** Severity: High because client was not included in the cycle's distribution run
** Component that failed: Fee Calculator

## Discreption
During the distribution run for period 2026-06-14 the pipeline failed due to run for client_id=C0453 as the fee percentage for this client was set to NULL. Resulting to batch missing 1 client. The fee calculator attempted to divide by zero for a null value which then caused an arithmetic in the calcuation. 

## Steps to reproduce failure
1. Set fee_pct to NULL for a client (any client or client C0453) in the SourceCalculations database 
2. Manually trigger the batch distribution run for period 2026-06-14 to observe error/behaviour 

## Observation
** ERROR BatchDistributionJob - Failed to process client_id=C0453, distribution skipped
** ERROR BatchDistributionJob - java.lang.ArithmeticException: / by zero at com.x.finance.distribution.FeeCalculator.applyFee(FeeCalculator.java:87)
** WARN  BatchDistributionJob - Client C0453 has fee_pct=NULL for period 2026-06
** INFO  BatchDistributionJob - Batch complete. 1 record failed, 4,811 succeeded.

## Business Impact 
Financial calculator not being able to process accurately and error handling allowing the batch to continiue running after skipping a client completely. And the final log message says "INFO  BatchDistributionJob - Batch complete. 1 record failed, 4,811 succeeded." does not make this seems like a big issue. Clients not receiving their money is a big deal for the business and can cause reputational harm, additional work for downstream teams to try to remedy the situation, calculation errors can cause delays in the distribution process and impact SLAs and other business processes that may be running at the time. 

## Proposed Resolution 
Enforce data schema contraints where null values are not accepted in the fee_pct or null values get defaulted to zero in the table. "  here is what I was reviewing Log Extract
2026-06-14 02:14:07 INFO  BatchDistributionJob - Starting distribution run for period 2026-06
2026-06-14 02:14:09 INFO  BatchDistributionJob - Loaded 4,812 client records for processing
2026-06-14 02:14:22 ERROR BatchDistributionJob - Failed to process client_id=C0453, distribution skipped
2026-06-14 02:14:22 ERROR BatchDistributionJob - java.lang.ArithmeticException: / by zero
    at com.x.finance.distribution.FeeCalculator.applyFee(FeeCalculator.java:87)
    at com.x.finance.distribution.DistributionProcessor.process(DistributionProcessor.java:142)
    at com.x.finance.distribution.BatchDistributionJob.run(BatchDistributionJob.java:64)
2026-06-14 02:14:22 WARN  BatchDistributionJob - Client C0453 has fee_pct=NULL for period 2026-06
2026-06-14 02:14:23 INFO  BatchDistributionJob - Continuing batch, 4,811 of 4,812 records processed successfully
2026-06-14 02:14:45 INFO  BatchDistributionJob - Batch complete. 1 record failed, 4,811 succeeded.
review the provided log extract and stack trace. Identify the likely root cause of the error, and write a clear, well-structured bug report as if logging it for a developer — include reproduction context, supporting evidence (referencing specific log lines or query logic), and business impact.
```