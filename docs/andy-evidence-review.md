# Andy Evidence Review

Andy supplied the following Phase 1 evidence:

- [Successful GitHub Actions run](https://github.com/DellyCodez/FindIt-SDSU/actions/runs/39181925718)
- [Testing branch](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests)
- [Database test module](https://github.com/DellyCodez/FindIt-SDSU/blob/test/database-tests/tests/test_database.py)
- ER diagram supplied separately by Andy

The test module covers email and date validation, empty-field rejection, lifecycle triggers, immutable claim identity, foreign-key enforcement, photo cascade behavior, and the one-approved-claim invariant. Andy's branch documentation reports 4,812 synthetic reports, zero foreign-key violations, 6/6 curated pairs in the top three, an indexed median of 0.051 ms, and a forced-scan median of 0.476 ms.

## Compatibility warning

The Andy evidence branch does not currently match the authoritative `work/app` schema:

- Andy's branch adds `visibility`, `contact_email`, and `submission_attempts`.
- It uses `color` and `file_name`/`mime_type`/`byte_count`.
- It documents migration version 8.
- `work/app` currently uses `primary_color`, `filename`, `width`, `height`, and `byte_size), with six tables and no `submission_attempts` table.

Alexander must confirm which schema is final and reconcile the branches before the ER diagram and QA results are described as verification of `work/app`. The report currently includes Andy's evidence as submitted branch evidence and clearly labels this mismatch.

The final package still needs Andy's verified JOIN, COUNT/GROUP BY, and filtering query output tied to the authoritative schema.
