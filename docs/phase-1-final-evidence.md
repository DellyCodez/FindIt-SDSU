# FindIt SDSU Phase 1 Final Evidence

The final technical source of truth is `work/unified-site` at commit `dcef14d2203995a0df7e69925c874345c6163743`.

## Final implementation

- Seven SQLite tables: `users`, `categories`, `locations`, `items`, `item_photos`, `claims`, and `submission_attempts`.
- SQLite schema version 8 with migrations preserving existing reports and claims.
- Protected admin review through `/admin/login`, password-hash verification, session authentication, and CSRF protection.
- Admin moderation can hide or restore reports without deleting their history.
- Public reporting and claiming use validation, a honeypot, upload checks, and SQLite-backed rate limits.
- Possible Matches use opposite-type, visible/open, same-category candidate filtering, a bounded date window, structured compatibility checks, and explainable scoring. Suggestions below 55 are hidden and at most three appear.
- The deployed website and all three team blog entries are complete.

## Final database evaluation

The final `docs/database-evaluation.md` reports:

- 4,812 synthetic reports in a temporary database.
- Zero foreign-key violations.
- Indexed candidate plan using `idx_items_match_candidates`.
- Indexed median: 0.051 ms over 200 warm-cache executions.
- Forced scan median: 0.476 ms.
- Six of six curated pairs retrieved in the top three.
- Incompatible iPhone/earbuds pair excluded.
- Approved claim returns the item, rejects the competing claim, and blocks a second approval.

## Andy's independent QA

Andy’s `test/database-tests` branch contains 30 test functions across database, matching, photo, stage 2/3, and web test files. The supplied GitHub Actions run reports 30/30 passing plus database evaluation success:

- [Verified Actions run](https://github.com/DellyCodez/FindIt-SDSU/actions/runs/39183211792)
- [Testing branch](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests)
- [Database tests](https://github.com/DellyCodez/FindIt-SDSU/blob/test/database-tests/tests/test_database.py)

The ER diagram supplied by Andy matches the final unified schema, including `submission_attempts`, visibility, contact email, and the final photo metadata fields.
