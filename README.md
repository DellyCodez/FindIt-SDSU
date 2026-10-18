# FindIt SDSU

A lost-and-found website we're building for our CS 514 database project at San Diego State University.

The idea is to give students one place to post items they've lost, report things they've found, and search for possible matches. We're starting with a small working version and will build on it throughout the semester.

## What we're building

For the first version, we want people to be able to:

- **Post a lost or found item** with a description, category, and campus location.
- **Browse and search reports** instead of going through individual posts.
- **View item details** and see whether an item is still available.
- **Submit a claim** when they think a found item belongs to them.
- **Review claims** through a simple demo page and mark returned items.
- **See possible matches** between public lost and found reports, with reasons to review each suggestion.

The claim process is the main feature we want to get right. A found item may have more than one claimant, but the system should only allow one approved claim.

## Database

The application uses six related SQLite tables: `users`, `items`, `categories`, `locations`, `claims`, and `item_photos`. This keeps reports organized and tracks who submitted each item and claim. Uploaded photo metadata is associated with reports; processed files live in an ignored local directory.

See [Database design](docs/database.md) for the implemented columns, relationships, and claim rules.

## Tech stack

The app uses **Python (Flask and Pillow), SQLite, HTML, CSS, and JavaScript**. Python's standard library supplies SQLite. Pillow validates and re-encodes report photos.

## Working on the project

We're splitting up the work so we can build different parts at the same time.

| Person | Branch | Working on |
| --- | --- | --- |
| Alexander | `work/app` | Website, backend, SQLite schema and database integration |
| Andy | `work/database` | Testing, sample data, ER diagram, SQL checks, and bug fixes |
| Samuel | `work/docs` | Project website, technical report, and presentation |

**Using AI to help?** ChatGPT, Gemini, Claude, and other tools can all use this repository for context. Start by giving the tool the GitHub link and asking it to read this README, [the database plan](docs/database.md), [the Phase 1 checklist](docs/phase-1.md), and [the temporary AI instructions](AGENTS.md). Tell it your name and branch—just connecting GitHub won't tell it which part you're responsible for.

Work in your own branch, keep changes to your part of the project, and don't push directly to `main`. When you're done, push your branch and open a pull request so we can review it before merging. Alexander is implementing the database; Andy will help test the schema and app before we merge everything.

## Run the Phase 1 app demo

The current app is a **local proof of concept** with fictional reports. Reports, claims, and review decisions are saved in an ignored SQLite file at `instance/findit.sqlite3` and survive server restarts. The demo reviewer page has no production authentication; use invented names and email addresses only.

Use Python 3.12. From the repository root on macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m app.init_db
.\.venv\Scripts\python.exe run.py
```

Open `http://127.0.0.1:5000/` in your browser. Stop the server with Ctrl+C. Re-running `app.init_db` keeps existing reports and claims; it adds the six fictional starter reports only to an empty database. Set `FINDIT_DB_PATH` before both initialization and launch to use a different SQLite file. Never commit a local `.sqlite3` file.

If you already have a local version 1 or 2 database, run `app.init_db` once before launching the updated app. Its in-place migrations add the matching index and `item_photos` table inside a transaction without replacing reports or claims. Back up your own database before any upgrade. Possible Matches appear on open item details when opposite-type reports have plausible public details. They are suggestions, not ownership decisions.

Reports can optionally include 1–3 JPEG, PNG, or WebP photos (8 MB per file, 25 MB total request). The server checks actual image content, limits pixel dimensions, corrects orientation, and writes re-encoded WebP files with randomized names to `instance/uploads/`. This directory and the SQLite file are ignored by Git. Set `FINDIT_UPLOAD_DIR` before both startup and later restarts if you need another local upload directory, and keep it together with the database when moving a demo. The photo route serves only files associated with an item in SQLite. Browsers with camera support can use the camera control on the report form.

To run the automated web and database checks on macOS or Linux:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

On Windows PowerShell, use `.\.venv\Scripts\python.exe` for both commands.

To reproduce the database evaluation on a **separate temporary database**, run:

```bash
.venv/bin/python -m database.evaluate
```

Windows PowerShell: `.\.venv\Scripts\python.exe -m database.evaluate`. The command prints JOIN and aggregate examples, query plans, indexed versus table-scan timings, curated fictional pair retrieval, and claim consistency checks. Results from one run are recorded in [the evaluation notes](docs/database-evaluation.md).

Try the demo in this order:

1. Browse the fictional lost and found reports; search by text and filter by report type, category, or location.
2. Report a **found** item with invented details. The new report opens automatically.
3. Claim the found item with an invented name, email, and identifying detail. The detail is private to the local reviewer screen.
4. Use **Demo reviewer** in the footer (or mobile menu) to approve or reject the claim. Approval marks the item returned and prevents a second approval.

The app has no login, email, or public deployment workflow. Photo uploads are for local fictional demonstrations only; do not expose this app publicly without authentication, abuse controls, and a security review. The starter campus and item pictures are generated demonstration imagery, not real lost property. Each new report uses a shared fictional demo reporter because there is no login. Andy will independently test the implemented database and app, then add the ER diagram, sample queries, and additional QA evidence.

## Progress

**Local proof of concept:** the Flask UI, SQLite-backed report and claim flow, explainable possible matches, responsive pages, local photo uploads and galleries, and integration tests are implemented. Production authentication and real student data are outside this local demonstration.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
