[Bug] BatchdistributionJob: ArithmeticException: division by zero where fee_pct is NULL for client C0453

** Severity: High (client was not included in the cycle's distribution run due to pipeline faulire)
** Component: Fee Calculator and data validation pipeline

## Description
During the distribution run for period 2026-06 BatchDistributionJob failed due to arithmetic issues for client_id=C0453 as the fee_pct for this client was set to NULL. This resulted in client not being included in this period's dictrubtion run. 

## Steps to reproduce failure
1. In SourceCalculations database set fee_pct to NULL for a client (any client or client C0453)
2. Manually trigger the batch distribution run for period 2026-06-14 to observe error/behaviour 

## Supporting Evidence
** ERROR BatchDistributionJob - Failed to process client_id=C0453, distribution skipped
** ERROR BatchDistributionJob - java.lang.ArithmeticException: / by zero at com.x.finance.distribution.FeeCalculator.applyFee(FeeCalculator.java:87)
** WARN  BatchDistributionJob - Client C0453 has fee_pct=NULL for period 2026-06
** INFO  BatchDistributionJob - Continuing batch, 4,811 of 4,812 records processed successfully
** INFO  BatchDistributionJob - Batch complete. 1 record failed, 4,811 succeeded.

## Business Impact 
** Financial impact: for client C0453 since they did not receive their fund
** Reputational Risk: and Operations overheard: Clients not receiving their money is a big deal for the business and in the age of social media it's easy for a disgruntled client to bring negative attention. Missed payments lead to addiditional work for operations team, calculation delays negatively impact SLAs and other business processed running at the same time. 
** Silent Failure:Final log says "INFO  BatchDistributionJob - Batch complete. 1 record failed, 4,811 succeeded." does not make this seems like a big issue which then cause alerting systems in place to not pick this failure up. 

## Proposed Resolution 
** Enforce data schema contraints where null values are not accepted in the fee_pct or null values get defaulted to 0.00 in the table. 
** Update FeeCalculator to handle for null values or zero value 
** Update BatchDistributionJob error handling to make this high priority error and fail silently