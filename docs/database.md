# Database design — implemented SQLite schema

`database/schema.sql` is the authoritative schema for the Flask app on `work/app`.
Initialize it with `python -m app.init_db` from the repository root, using the
project virtual environment. The ignored local file is `instance/findit.sqlite3`.
Initialization is repeatable: it preserves existing reports and claims and inserts
six fictional reports only if the `items` table is empty. `FINDIT_DB_PATH` can point
both initialization and app startup at another SQLite file.

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
.venv/bin/python run.py
```

See the README for Windows PowerShell commands. Andy can use this schema as the
source of truth for an ER diagram, independent QA, fictional sample data, and
verified JOIN, filter, and GROUP BY queries. Those supporting deliverables are
separate from the authoritative schema.
