# Database design — implemented SQLite schema

`database/schema.sql` is the authoritative schema for the Flask app on `work/app`.
Initialize it with `python -m app.init_db` from the repository root, using the
project virtual environment. The ignored local file is `instance/findit.sqlite3`.
Initialization is repeatable: it preserves existing reports and claims and inserts
six fictional reports only if the `items` table is empty. `FINDIT_DB_PATH` can point
both initialization and app startup at another SQLite file.
An existing version 1 database is upgraded in place to version 2 by
`database/migrations/002_match_candidates.sql`; the transaction adds one index
and preserves every report and claim. The initializer records the version in
SQLite's `user_version` pragma. It refuses unknown versions and nonempty
unversioned databases instead of rebuilding them.

## Tables and columns

| Table | Columns | Purpose |
| --- | --- | --- |
| `users` | `id` PK, `name`, `email` | Fictional reporter and claimant identities; email is unique without case sensitivity. |
| `categories` | `id` PK, `name` | One category name per row. |
| `locations` | `id` PK, `name` | One campus location name per row. |
| `items` | `id` PK, `reporter_id` FK, `category_id` FK, `location_id` FK, `title`, `description`, `kind`, `status`, `report_date`, `image_key` | Lost/found reports. `image_key` selects one of the local demo pictures or is null. |
| `claims` | `id` PK, `item_id` FK, `claimant_id` FK, `explanation`, `status`, `created_at` | Private identifying explanations and review decisions for found items. |

Each foreign key references the named table's `id` and restricts deletion of a
referenced row. The app enables `PRAGMA foreign_keys = ON` for **every** SQLite
connection. One user can report many items and submit many claims. Each item has
one category, one location, and one reporter; a found item can have many claims.
Category and location names live in their own tables instead of being copied into
each item. The app joins these tables when it displays reports.

## Validation and claim integrity

Required text fields have `NOT NULL` and length checks. `items.kind` is `Lost` or
`Found`; `items.status` is `Open` or `Returned`, with `Returned` allowed only for a
found item. `claims.status` is `Pending`, `Approved`, or `Rejected`. Dates use
`YYYY-MM-DD`. Form validation gives people useful messages, while the SQLite
constraints also reject invalid direct inserts.

The partial unique index `one_approved_claim_per_item` permits at most one
`Approved` claim per item. A trigger permits new claims only for open found items.
Another trigger checks approval eligibility. When a claim is approved, an SQLite
trigger marks its item `Returned` and rejects its other pending claims in the same
transaction. Triggers prevent returning an item without an approved claim or
reopening an approved item. The app's `review_claim` operation uses
`BEGIN IMMEDIATE` so competing reviewers serialize their decisions. A rejected or
approved claim cannot be reviewed again. A claim's item and claimant cannot be
changed, and an approved claim cannot be deleted. An item with claims cannot
change from found to lost.

## Possible-match lookup

For an open report, the app queries **open reports of the opposite type in the
same category**. It considers a found date from two days before to 45 days
after a lost date; the reverse window is used from a found report. The composite
index `idx_items_match_candidates(kind, status, category_id, report_date)`
supports this bounded candidate lookup. The query joins categories and
locations for display, then Python scores up to 300 recent candidates using
only public titles, descriptions, dates, and locations.

The score gives 35 points for the matching category, 18 for the same location,
2–15 for date proximity, and up to 30 for shared meaningful words. It requires
at least one shared non-color word, filters conflicting stated colors, and
requires two shared words for the broad `Other` category. Only suggestions
scoring at least 60 are shown, up to three per report. Reasons explain the
visible evidence. Claimant names, contact information, and private explanations
are never read by the
matching query. Suggestions are **not** ownership proof. The rule can miss
misclassified items or records beyond its time and candidate limits, and it
can still suggest unrelated items with similar public descriptions.

Claim names, emails, and private explanations are queried only for the local
demo reviewer page. Public item queries do not select this information. The
reviewer has **no production authentication**; use fictional information and do
not deploy it as a real claims service.

## Local setup and tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m app.init_db
.venv/bin/python -m pytest -q app/test_web.py
.venv/bin/python -m pytest -q app/test_matching.py
.venv/bin/python -m database.evaluate
.venv/bin/python run.py
```

See the README for Windows PowerShell commands. Andy can use this schema as the
source of truth for an ER diagram, independent QA, fictional sample data, and
verified JOIN, filter, and GROUP BY queries. Those supporting deliverables are
separate from the authoritative schema.
