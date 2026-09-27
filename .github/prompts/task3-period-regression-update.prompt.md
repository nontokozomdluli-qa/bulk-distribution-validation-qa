---
name: task3-period-regression-update
description: "Update Task 3 period logic/tests/docs and verify with a focused Playwright run"
argument-hint: "Describe the Task 3 update needed (example: TEST_PERIOD should map transaction checks to next month and log totals)"
agent: agent
---
You are working in this repository's Task 3 Playwright suite.

Goal:
Implement the requested Task 3 regression update end-to-end, including code changes, documentation updates, and verification.

Inputs:
$ARGUMENTS

Primary files to check:
- [task 3/tests/distribution-transactions.spec.js](../task%203/tests/distribution-transactions.spec.js)
- [task 3/tests/status-check-flow.mocked.spec.js](../task%203/tests/status-check-flow.mocked.spec.js)
- [task 3/README.md](../task%203/README.md)
- [task 3/package.json](../task%203/package.json)

Required workflow:
1. Parse the request from $ARGUMENTS and identify exact behavior changes needed.
2. Update only the minimum necessary files under Task 3.
3. Keep existing default behavior intact unless the request explicitly changes it.
4. If period-selection logic is touched:
   - Preserve explicit override priority.
   - Validate YYYY-MM format when deriving dates.
   - Handle year rollovers correctly when calculating next month.
5. If logging/reporting is requested:
   - Add concise console output with clear labels.
   - Include selected periods and relevant totals/counts.
6. Update [task 3/README.md](../task%203/README.md) so run instructions match the current behavior.
7. Run a focused verification command from Task 3 (for example, `npm run test:period -- 2026-06 tests/distribution-transactions.spec.js` when period logic is involved).
8. Report outcomes clearly, including whether failures are expected seeded-data anomalies or regressions introduced by the change.

Response format:
- Summary: one short paragraph on what changed.
- Files changed: list each file and what was updated.
- Verification: command(s) run and key result lines.
- Notes: any assumptions, open questions, or optional follow-ups.

Constraints:
- Do not refactor unrelated code.
- Do not remove existing tests unless explicitly requested.
- Keep edits ASCII-only unless a file already requires Unicode.
