# FindIt SDSU Phase 1 Technical Report Source

This source is based on the authoritative `work/app` branch at commit `6f6321e`. The application is a Flask and SQLite proof of concept using fictional data. The six implemented tables are `users`, `categories`, `locations`, `items`, `item_photos`, and `claims`.

## Core findings

- SQLite persistence replaces process-local storage for normal runs.
- Every connection enables foreign keys.
- Items reference reporters, categories, and locations.
- Item photos store metadata in SQLite and processed WebP files in an ignored local directory.
- Claims begin Pending and may target only an open Found item.
- A partial unique index allows at most one Approved claim per item.
- Approval triggers mark the item Returned and reject other pending claims.
- Possible Matches use SQL candidate filtering followed by explainable Python scoring.
- The repository documents a 24-test application run and a separate synthetic evaluation of 4,815 reports.

## Evidence boundary

Andy’s independent QA, SQL verification, and final ER diagram are not present on `work/app` at the time of this draft. The report must be updated with those artifacts before the submission is described as final.
