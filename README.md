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

The application uses five related SQLite tables: `users`, `items`, `categories`, `locations`, and `claims`. This keeps reports organized and tracks who submitted each item and claim.

See [Database design](docs/database.md) for the implemented columns, relationships, and claim rules.

## Tech stack

The app uses **Python (Flask), SQLite, HTML, CSS, and JavaScript**. Flask is the only runtime package; Python's standard library supplies SQLite.

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

If you already have a local database from the first SQLite version, run `app.init_db` once before launching the updated app. It adds the matching lookup index in a transaction without replacing reports or claims. Possible Matches appear on open item details when opposite-type reports have plausible public details. They are suggestions, not ownership decisions.

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

The app has no login, uploads, email, or public deployment workflow. The campus and item pictures are generated demonstration imagery, not real lost property. Each new report uses a shared fictional demo reporter because there is no login. Andy will independently test the implemented database and app, then add the ER diagram, sample queries, and additional QA evidence.

## Progress

**Phase 1 proof of concept:** the Flask UI, SQLite-backed report and claim flow, explainable possible matches, responsive pages, and integration tests are implemented. Production authentication and real student data are outside this local demonstration.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
