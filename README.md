# FindIt SDSU

A unified Flask lost-and-found website and project presentation for our CS 514 database project. It is an independent student project, not an official SDSU service.

Visitors can explore fictional reports and learn about the team, product, blog, and resources in one website. Presenter-only forms demonstrate reporting, matching, and claim review.

## What we're building

For the first version, we want people to be able to:

- **Post a lost or found item** with structured details, a campus location, and up to three optional photos.
- **Browse and search reports** instead of going through individual posts.
- **View item details** and see whether an item is still available.
- **Submit a claim** when they think a found item belongs to them.
- **Review claims** through a simple demo page and mark returned items.
- **See possible matches** between public lost and found reports, with reasons to review each suggestion.
- **Read About, Our Product, Blog, and Resources** alongside the real application.

The claim process is the main feature we want to get right. A found item may have more than one claimant, but the system should only allow one approved claim.

## Database

The application uses six related SQLite tables: `users`, `items`, `categories`, `locations`, `item_photos`, and `claims`. This keeps reports organized, associates processed photos with reports, and tracks claims.

See [Database design](docs/database.md) for the implemented columns, relationships, and claim rules.

## Tech stack

The app uses **Python (Flask and Pillow), SQLite, HTML, CSS, and JavaScript**. Pillow validates and re-encodes uploads; Python's standard library supplies SQLite.

## Working on the project

We're splitting up the work so we can build different parts at the same time.

| Person | Branch | Working on |
| --- | --- | --- |
| Alexander | `work/app` | Website, backend, SQLite schema and database integration |
| Andy | `work/database` | Testing, sample data, ER diagram, SQL checks, and bug fixes |
| Samuel | `work/docs` | Project website, technical report, and presentation |
| Integration | `work/unified-site` | Unified Flask website and PythonAnywhere preparation |

**Using AI to help?** ChatGPT, Gemini, Claude, and other tools can all use this repository for context. Start by giving the tool the GitHub link and asking it to read this README, [the database plan](docs/database.md), [the Phase 1 checklist](docs/phase-1.md), and [the temporary AI instructions](AGENTS.md). Tell it your name and branch—just connecting GitHub won't tell it which part you're responsible for.

Work in your own branch, keep changes to your part of the project, and don't push directly to `main`. When you're done, push your branch and open a pull request so we can review it before merging. Alexander is implementing the database; Andy will help test the schema and app before we merge everything.

## Run the unified website locally

The local development app uses fictional reports. Reports, claims, and review decisions are saved in an ignored SQLite file at `instance/findit.sqlite3` and survive server restarts. Development mode binds to loopback and permits the demo forms without a presenter password. **Public mode requires a password hash and Flask secret key** and protects reporting, claims, and review. See [PythonAnywhere deployment](docs/pythonanywhere.md).

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

If you already have a local database, run `app.init_db` once before launching the updated app. It migrates older schemas through version 6 in a transaction without replacing reports or claims, including the published v4 photo and color columns. Processed WebP photos live in the ignored `instance/uploads/` directory beside the database. Back up the SQLite file and its uploads directory together. Possible Matches appear on open item details when opposite-type reports have plausible public details. The score is similarity, not an ownership probability.

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
3. Claim the found item with an invented name, email, and identifying detail. The detail is private to the presenter review screen.
4. Open **Review** after presenter sign-in, or go to `/review/claims` in the local demo, to approve or reject the claim. Approval marks the item returned and prevents a second approval.

The public configuration uses a single presenter password to protect reporting, claims, and review. It does not provide student accounts or email delivery; use fictional contact information only. Public item pages and matching results exclude the separate report contact email and private claim explanations. The campus and starter item pictures are generated demonstration imagery, not real lost property. Each new report uses a shared fictional demo reporter because there is no student login. Andy will independently test the implemented database and app, then add the ER diagram, sample queries, and additional QA evidence.

## Progress

**Unified Phase 1 prototype:** the Flask UI, project pages, SQLite-backed report and claim flow, presenter gate, explainable possible matches, responsive pages, and integration tests are implemented. Real student data and production-grade account management remain outside this classroom demonstration.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
