# Testing plan — Phase 1

**QA owner:** Andy. **Implementation support:** Alexander.

Record test date, commit SHA, environment, outcome and reproduction notes when running tests. This page is a plan; **no tests are claimed to have passed yet**.

| ID | Check | Expected outcome |
| --- | --- | --- |
| T-01 | Fresh schema + fictional seed | Tables, constraints and sample reports create cleanly. |
| T-02 | Foreign keys | Invalid reporter, category, location or claimant reference is rejected. |
| T-03 | Lost report | Item persists and reappears after restarting the app. |
| T-04 | Found report | Item persists with the correct type and location. |
| T-05 | Search/filter | Keyword, category, location and type filters return matching records only. |
| T-06 | Empty/invalid input | Meaningful validation error; database remains unchanged. |
| T-07 | Claim valid found item | New pending claim references correct found item and user. |
| T-08 | Claim a lost/returned item | Operation is refused without modifying claim records. |
| T-09 | Approve claim | Selected claim becomes approved, other pending claims are resolved, item becomes returned. |
| T-10 | Duplicate approval | Database invariant prevents a second approved claim. |
| T-11 | Dashboard aggregates | Counts match a manual SQL verification query. |
| T-12 | Privacy | Public views do not reveal `private_details`. |
| T-13 | Demo walkthrough | End-to-end report → search → claim → review works without unexplained manual edits. |

## Evidence to collect

- ER diagram matched to actual DDL.
- Executed CREATE TABLE and seed scripts.
- Representative JOIN, GROUP BY and transaction queries with expected/actual output.
- Test output logs (sanitized), screenshots and known limitations.
- Optional query-plan comparison only after real measurements exist.

## Evaluation dataset

Andy prepares synthetic sample users, multiple campus-style locations, several categories, both lost and found reports, and claims in different states. Keep a repeatable generator/seed script so a fresh clone can reproduce the demo.

Use an appropriately sized synthetic dataset for join/filter and index measurements when time allows. Record actual counts and timings, rather than guessing.

## Bug workflow

Create a GitHub issue using the bug template. Include steps, expected/actual results, severity and fictional example IDs. Alexander fixes application defects; Andy verifies the fix and records the commit tested.
