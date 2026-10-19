# FindIt SDSU — initial database planning

This branch preserves the early database-planning milestone for FindIt SDSU, a campus lost-and-found project developed for SDSU CS 514.

**Current database schema and running application:** [`work/unified-site`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) · [Live prototype](https://finditsdsu.pythonanywhere.com/) · [Independent QA](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests)

## Project overview

FindIt combines structured lost and found reports, searchable categories and locations, possible-match suggestions, and a review process for ownership claims.

The original model separated `users`, `items`, `categories`, `locations`, and `claims`. The implemented schema later expanded to seven tables, including `item_photos` and `submission_attempts`. For the authoritative field definitions, relationships and constraints, consult [the current database documentation](https://github.com/DellyCodez/FindIt-SDSU/blob/work/unified-site/docs/database.md) rather than this early snapshot.

## Team contributions

- **Alexander Hills:** Flask application and SQLite integration.
- **Andy Thai:** Database modeling, ER diagram and independent SQL verification.
- **Samuel Shadi:** Documentation and presentation.

This branch is retained for development history. It is **not** the current runnable application.

*Independent CS 514 student project; not an official SDSU service.*
