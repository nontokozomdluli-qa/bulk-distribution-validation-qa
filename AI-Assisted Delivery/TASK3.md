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

## Actual prompts

### Core test requirements
1. **All distributions completed**: Verify status = COMPLETED in Distributions table for selected period.
2. **All transactions approved**: Verify status = APPROVED in Transactions table for selected period (derived from transaction_date as YYYY-MM).
3. **No completed without approved**: Check that no COMPLETED distribution exists without an APPROVED transaction for the same period.
4. **Client presence**: Verify each client in Distributions exists in Transactions for the same distribution/client linkage.
5. **No rejected distributions**: Ensure no COMPLETED distribution has REJECTED transaction status.
6. **No pending distributions**: Ensure no COMPLETED distribution has PENDING transaction status.
7. **Missing period validation**: Return not-found error when requesting distribution period for a client that doesn't exist.
8. **Invalid client ID format**: Return validation error for client IDs not matching format "Letter+Numbers" (e.g., C101).

### Period selection behavior
- **Default**: Automatically use latest YYYY-MM from Transactions.transaction_date
- **Distribution period**: Latest from Distributions.period
- **Manual override via TEST_PERIOD**: 
  - Sets distributionPeriod = TEST_PERIOD
  - Automatically sets transactionPeriod = next month of TEST_PERIOD
- **Individual overrides**: Set DISTRIBUTION_PERIOD and/or TRANSACTION_PERIOD independently
- **Console logging**: Print periods used, amounts, and row counts for each run

### Implementation requirements
- Use SQLite database queries for all validations
- Implement mocked status-check flow (no external dependencies)
- Environment variable-driven period selection
- Default latest-period fallback if no manual period provided
- Comprehensive test coverage spanning positive and negative cases

### npm script shortcuts
- `npm test` - Run all tests with default periods
- `npm run test:period -- 2026-06` - Set TEST_PERIOD to 2026-06 and run tests
- Manual period examples:
  - PowerShell: `$env:TEST_PERIOD='2026-05'; npm test`
  - Bash: `TEST_PERIOD=2026-05 npm test`

### Regression strategy priorities
- **High priority (Tests 1–3)**: Critical business flows for distribution completion and transaction approval verification
- **Medium priority (Tests 4–6)**: Additional safety checks for client and status consistency
- **Edge cases (Tests 7–8)**: Input validation and missing data handling

### README content
- Include all 8 tests documented
- Provide period selection examples
- Show manual test execution options
- Format for easy CI/CD integration (automated regression suite ready)
** For task 3 the files will be stored in folder task 3. I want to build automating testing using for these Distributions and Transactions. Using Plyawright. These are the following tests that I want to cover. test 1 All distributions completed for period (take the value of that period) (looking at the status in Distributions Tables). If status is Completed pass. test 3 All distributions Approved. Get the status from Transactions table. If status is Approved test should pass otherwise fail. Also look at current period (transaction date and only take year and Month e.g 2026-05). test 3 Distribution completed but transaction not approved. For the period at distributions with Compeled status in Distributions table but do not have Approved status in Transaction db. If found test must fail otherwise pass. test 4 Client missing from distribution. Check the client lict for a distribution period in the distributions table and see if the client is in the transactions table. test 5 Failed distribution. Status says Complete in distribution table but says Rejected in Transaction Table. test 5. Pending Distribution. Status says Completed in distribution table but says pending in transaction table.
** Looking at tests added do they cover everything here or do I need to add other tests "X wants to strengthen automated regression coverage for its client distribution flow ahead of the next release, and wants to raise the automation capability of the wider QA team.
Automate testing for the client distribution status-check flow: given a client ID and period, the system returns the distribution status (e.g., PENDING, COMPLETED, FAILED) and the distributed amount. All interactions must be fully mocked/simulated so the solution runs locally with zero external dependencies.Use TestSigma, Selenium, Playwright, or an equivalent tool of your choice.
Cover 4–5 scenarios (not an exhaustive suite) spanning positive and negative/edge cases — for example: a completed distribution, a distribution still pending, an invalid client ID, a missing period, or a failed distribution. Structure your tests so they could realistically run as part of a regression suite; detailed CI pipeline configuration is not required.
"
** add a missing distribution period test. add an invalid client ID test, Client ID must start with C or should be a letter with numbers.
** this file should only have The regression strategy information. Look at my proposed regression strategy and compare we task requirement and point out if I am missing anything.  ## Context
With the release happening in 2 days there isn't enough time to test everything. Business critical flows must be validate to ensure financial correctness and business reporting. Manual testing will be used to spot check and do exploratory testing for edge cases.

Regression strategy
High priority
** Automation coverage focus: Test 1 - 3 as they focus on critical business flows which is to ensure that distribution flows runs and finishes correctly. Validate financial correctness for downstream reporting and reconciling activities. Compare main tables to ensure that distributions are in correct status in both tables.
** Manual checks: Look out for edge cases such as unusually large amounts, exploratory check error handling.

Do not cover
** Do not cover performance testing for this release because of time constraints. Monitor is production and use past performance to inform decision.
** Low likelihood and can be verified by monitoring in production post release.

Automate if time allows (Medium to Low risk):
** Test 4 -8 do not need to run for this release and can run later. They are there to provide the additional safety and some of the tests would have been covered by validation done for task 1

Automated Coverage Reflecting prioritization
Test 1 - Test 3 are critical for regression and must run
Test 4 - Test 8 provide additional safety but can be prioritised. Partially covered in task 1
Manual testing focusing on highly likely edge cases, focus on error handling complements error automation by focusing on a different but equally important task. Evrything else should move to README.md and ensure that all tests are included in the readme file and format files
** can I manually input period so that I can manipulate the tests. If period is null tests should run the way they are running but if period is inputed test should use that period. add an npm script shortcut like:
test:period with TEST_PERIOD passed inline.
** when date is set manually transactionPeriod should automatically look at following month like how it does for npm run test distributionPeriod: 2026-06
transactionPeriod: 2026-07. let's also log the amounts for ease of reference 
** with run also add an example of command with manual period set