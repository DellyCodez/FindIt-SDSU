# Database design — implemented SQLite schema

`database/schema.sql` is the authoritative schema for the Flask app on `work/unified-site`.
Initialize it with `python -m app.init_db` from the repository root, using the
project virtual environment. The ignored local file is `instance/findit.sqlite3`.
Initialization is repeatable: it preserves existing reports and claims and inserts
six fictional reports only if the `items` table is empty. `FINDIT_DB_PATH` can point
both initialization and app startup at another SQLite file.
An existing version 1–7 database is upgraded in place through migrations
`002_match_candidates.sql` to `008_report_visibility.sql`. The transaction
preserves every existing report and claim. The published `work/app` version 4
used `primary_color`, `filename`, and `byte_size`; the initializer adds the
unified color field and renames the photo columns in place while retaining the
original data. The initializer records version 8 in
SQLite's `user_version` pragma. It refuses unknown versions and nonempty
unversioned databases instead of rebuilding them.

## Tables and columns

| Table | Columns | Purpose |
| --- | --- | --- |
| `users` | `id` PK, `name`, `email` | Fictional reporter and claimant identities; email is unique without case sensitivity. |
| `categories` | `id` PK, `name` | One category name per row. |
| `locations` | `id` PK, `name` | One campus location name per row. |
| `items` | `id` PK, reporter/category/location FKs, `title`, `description`, `kind`, `status`, `visibility`, `report_date`, `image_key`, `item_type`, `brand`, `model`, `color`, `distinguishing_features`, `contact_email` | Lost/found reports with structured matching fields. `contact_email` is excluded from public queries; `visibility` lets an admin hide a report without deleting history. |
| `item_photos` | `id` PK, `item_id` FK, randomized `file_name`, `position`, MIME type, dimensions, byte count | Up to three processed WebP photos per report; files are stored in an ignored local directory. |
| `claims` | `id` PK, `item_id` FK, `claimant_id` FK, `explanation`, `status`, `created_at` | Private identifying explanations and review decisions for found items. |
| `submission_attempts` | `id` PK, `action`, keyed `actor_key`, `created_at` | Atomic rolling-window limits for report, claim, and admin-login POSTs; no raw IP address is stored. |

Each foreign key references the named table's `id`; deleting an item cascades to
its photo metadata, while other references restrict deletion. The app enables `PRAGMA foreign_keys = ON` for **every** SQLite
connection. One user can report many items and submit many claims. Each item has
one category, one location, and one reporter; a found item can have many claims.
Category and location names live in their own tables instead of being copied into
each item. The app joins these tables when it displays reports. Photo positions
are unique per item and constrained to 1–3. Image files must be backed up with
the SQLite file; SQLite cannot make filesystem writes transactional.

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
supports this bounded candidate lookup; `idx_items_match_type` supports queries
that also constrain the structured item type. The query joins categories and
locations for display, then Python scores up to 300 recent candidates using
only public titles, descriptions, dates, locations, type, brand, model, and color.

<<<<<<< HEAD
Alexander will implement the schema, exact columns and SQLite integration on `work/app`. Andy will review the schema, prepare fictional seed data and an ER diagram, and write database tests and sample queries on `work/database` using the approved column names. This page is still a design draft, not completed SQL code.
=======
The score gives 20 points for category, 22 for same item type, 12 for location,
2–10 for date proximity, up to 20 for meaningful shared details, and additional
points for matching brand, model, and color. Conflicting known item types,
brands, models, and colors are excluded. Generic words such as “case” and
colors do not count as distinctive shared details. Suggestions must score at
least 55; at most three appear by default. Reasons explain the visible evidence.
Claimant names, contact information, and private explanations are never read by the
matching query. Suggestions are **not** ownership proof. The rule can miss
misclassified items or records beyond its time and candidate limits, and it
can still suggest unrelated items with similar public descriptions.

Claim names, emails, report contact emails, and private explanations are queried only for the
authenticated reviewer page. Public item queries do not select this information. In
public mode, reporting and claiming are open to visitors; claim review requires the
admin password. An admin can hide or restore reports through `/admin/items`;
hidden reports, their photos, and their matches are removed from public pages.
Submission attempts are reserved inside `BEGIN IMMEDIATE` so
concurrent requests share the same limit. Entries older than a day are removed
opportunistically. Limits are four reports or eight claims per hour, and ten
admin-login attempts per 15 minutes, per IP digest. This is a prototype safeguard,
not student account management or full spam moderation.

## Local setup and tests

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m app.init_db
.venv/bin/python -m pytest -q app/test_web.py
.venv/bin/python -m pytest -q app/test_matching.py
.venv/bin/python -m pytest -q app/test_photos.py
.venv/bin/python -m database.evaluate
.venv/bin/python run.py
```

See the README for Windows PowerShell commands. Andy can use this schema as the
source of truth for an ER diagram, independent QA, fictional sample data, and
verified JOIN, filter, and GROUP BY queries. Those supporting deliverables are
separate from the authoritative schema.
>>>>>>> origin/work/unified-site
