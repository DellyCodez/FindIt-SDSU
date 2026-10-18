# Database design — implemented SQLite schema

`database/schema.sql` is the authoritative schema for the Flask app on `work/app`.
Run `python -m app.init_db` before starting Flask. The default SQLite file is
`instance/findit.sqlite3`; `FINDIT_DB_PATH` selects another file. Initialization
is repeatable. It seeds six fictional reports only when `items` is empty.

## Tables and relationships

| Table | Main columns | Relationship |
| --- | --- | --- |
| `users` | `id`, `name`, unique case insensitive `email` | One user may report many items and submit many claims. |
| `categories` | `id`, unique `name` | One category per item. |
| `locations` | `id`, unique `name` | One location per item. |
| `items` | `id`, reporter/category/location FKs, `kind`, `status`, `title`, `description`, `report_date`, `image_key`, `item_type`, `brand`, `model`, `primary_color`, `distinguishing_features` | Each report belongs to a reporter, category, and location. |
| `item_photos` | `id`, `item_id` FK, `position`, `filename`, dimensions, byte size | Up to three photos per item, ordered by position. |
| `claims` | `id`, item/claimant FKs, private `explanation`, `status`, `created_at` | A found item may have many claimants but only one approved claim. |

The new item attributes are nullable for older reports; the initializer never
guesses and writes missing details into existing rows. The current report form
requires an item type and primary color and validates type choices against the
selected category. Brand, model, and distinguishing features are optional.
The legacy Keys category remains, and Accessories is available for new reports.

Every database connection enables `PRAGMA foreign_keys = ON`. SQLite checks
required values, status values, text lengths, date shape, photo slots, and
referential integrity. The partial unique index `one_approved_claim_per_item`
permits at most one approved claim for each item.

## Migration and photo storage

The initializer records schema version **4** in `PRAGMA user_version`.
A version 1 database applies migrations 002, 003, and 004; version 2 applies
003 and 004; version 3 applies 004. A version 4 database only repeats safe
initialization. Migrations run inside a transaction and preserve reports,
claims, users, and photo rows. Unknown versions and nonempty unversioned
databases are refused rather than reset.

Migration 004 adds five nullable item columns and an item type candidate index.
It does not rewrite primary keys or foreign keys. The `item_photos` table has
a unique `(item_id, position)` pair and checks positions 1–3. Uploaded JPEG,
PNG, or WebP files are validated and re-encoded as WebP with random filenames.
SQLite stores their metadata; the actual files remain in the ignored
`instance/uploads/` directory or `FINDIT_UPLOAD_DIR`. Back up or move the
database and upload directory together. The first photo is used on listing
cards; the item page displays the full gallery.

## Matching

SQL fetches open reports of the opposite kind in the same category within a
bounded date window. A found report may be from two days before through 45
days after a lost report; the reverse window applies to found reports. Where
the source has an explicit item type, SQL accepts that type and legacy reports
without a type (or with Other). The composite
`idx_items_match_candidates(kind, status, category_id, report_date)` index
supports the date lookup. At most 300 recent candidates enter Python scoring.

Python cautiously recognizes an older report's type from an unambiguous title
without storing the guess. Known incompatible types, conflicting colors, and
conflicting known brands or models are rejected. A candidate needs shared
distinctive details or a matching model; generic terms such as “case”,
“black”, and “item”, plus the shared location, cannot make a lead by themselves.
Reports without recognized types need more shared details.

The heuristic starts with 20 points for category, adds 34 for two compatible
recognized types (or 6 for one known type), up to 24 for distinctive words,
8 for color, 10 for brand, 16 for model, 6 for location, and up to 7 for date
proximity. Scores are capped at 100; suggestions below 58 are hidden and at
most three appear. Reasons describe public evidence. **Scores are similarity
heuristics, not ownership probabilities or proof.** Wrong categories, sparse
descriptions, and the date window can hide real matches; similar public clues
can still produce a false lead. The algorithm never reads claim evidence or
claimant contact information.

## Claims and privacy

A claim starts Pending and can target only an open found item. The application
rejects a second claim from the same email for that item without removing
existing legacy duplicates. A reviewer can approve or reject a pending claim
once. `review_claim` uses `BEGIN IMMEDIATE`, and SQLite triggers atomically
mark an approved item's status Returned and reject its other pending claims.
Triggers prevent reopening an approved item, deleting its approval, or changing
the item or claimant attached to a claim.

Public report forms reject common email addresses and phone numbers in public
text with a message directing the writer to the claim form. Public item and
matching queries do not select claimant names, emails, or explanations. The
reviewer route accepts loopback requests only, but **has no authentication**:
anyone with local access can see fictional claim details. Do not deploy it as
a real claims service.

## Reproduce the checks

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m database.evaluate
```

The database evaluation uses a separate disposable database. See
[database-evaluation.md](database-evaluation.md) for its measured results and
limits. The README has Windows PowerShell setup commands. The course ER diagram
and independent QA from the database teammate remain separate deliverables.
