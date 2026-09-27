## Context 
With the release happening in 2 days there isn't enough time to test everything. Business critical flows must be validate to ensure financial correctness and business reporting. Manual testing will be used to spot check and do exploratory testing for edge cases. 

## Regression strategy 

High priority
- Automation coverage focus: Test 1 - 3 as they focus on critical business flows which is to ensure that distribution flows runs and finishes correctly. Validate financial correctness for downstream reporting and reconciling activities. Compare main tables to ensure that distributions are in correct status in both tables. 
- Manual checks: Look out for edge cases such as unusually large amounts, exploratory check error handling. 

Do not cover
- Do not cover performance testing for this release because of time constraints. Monitor is production and use past performance to inform decision.
- Low likelihood and can be verified by monitoring in production post release.

Automate if time allows (Medium to Low risk):
- Test 4 -8 do not need to run for this release and can run later. They are there to provide the additional safety and some of the tests would have been covered by validation done for task 1

Automated Coverage Reflecting prioritization
** Test 1 - Test 3 are critical for regression and must run 
** Test 4 - Test 8 provide additional safety but can be prioritised. Partially covered in task 1 
** Manual testing focusing on highly likely edge cases, focus on error handling complements error automation by focusing on a different but equally important task
