# FindIt SDSU

A unified Flask lost-and-found website and project presentation for our CS 514 database project. It is an independent student project, not an official SDSU service.

Visitors can browse, post lost or found reports with photos, and submit private claims without signing in. The password-protected admin area is reserved for claim review.

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

The application uses seven SQLite tables: `users`, `items`, `categories`, `locations`, `item_photos`, `claims`, and `submission_attempts`. The last table supports limits on public form submissions; it stores keyed IP digests, never raw IP addresses.

See [Database design](docs/database.md) for the implemented columns, relationships, and claim rules.

## Tech stack

The app uses **Python (Flask and Pillow), SQLite, HTML, CSS, and JavaScript**. Pillow validates and re-encodes uploads; Python's standard library supplies SQLite.

## Working on the project

We're splitting up the work so we can build different parts at the same time.

| Person | Branch | Working on |
| --- | --- | --- |
| Alexander | `work/app` | Website, backend, SQLite schema and database integration |
| Andy | `work/database` | Testing, sample data, ER diagram, SQL checks, and bug fixes |
<<<<<<< HEAD
| Samuel | `work/docs` | Project website, technical report, and presentation |
=======
| Samueel Shadi | `work/docs` | Project website, technical report, and presentation |
| Integration | `work/unified-site` | Unified Flask website and PythonAnywhere preparation |
>>>>>>> origin/work/unified-site

**Using AI to help?** ChatGPT, Gemini, Claude, and other tools can all use this repository for context. Start by giving the tool the GitHub link and asking it to read this README, [the database plan](docs/database.md), [the Phase 1 checklist](docs/phase-1.md), and [the temporary AI instructions](AGENTS.md). Tell it your name and branch—just connecting GitHub won't tell it which part you're responsible for.

Work in your own branch, keep changes to your part of the project, and don't push directly to `main`. When you're done, push your branch and open a pull request so we can review it before merging. Alexander is implementing the database; Andy will help test the schema and app before we merge everything.
<<<<<<< HEAD
=======

## Run the unified website locally

The local development app uses fictional reports. Reports, claims, and review decisions are saved in an ignored SQLite file at `instance/findit.sqlite3` and survive server restarts. Development mode binds to loopback. **Public mode requires a password hash and Flask secret key.** Reporting and claiming stay public; only claim review requires admin sign-in. Public POST forms use CSRF validation, a honeypot, server-side validation, upload checks, and SQLite-backed rate limits. See [PythonAnywhere deployment](docs/pythonanywhere.md).

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

If you already have a local database, run `app.init_db` once before launching the updated app. It migrates older schemas through version 8 in a transaction without replacing reports or claims, including the published v4 photo and color columns. Processed WebP photos live in the ignored `instance/uploads/` directory beside the database. Back up the SQLite file and its uploads directory together. Possible Matches appear on open item details when opposite-type reports have plausible public details. The score is similarity, not an ownership probability.

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
4. Open `/admin/claims` and sign in as the reviewer to approve or reject the claim. Approval marks the item returned and prevents a second approval. `/admin/items` lets the same reviewer hide or restore a public report without deleting its history.

The public configuration uses a single admin password for private claim review and report moderation. It does not provide student accounts, automatic screening, ownership verification, or email delivery; use fictional contact information only until operational safeguards are added. Public item pages and matching results exclude the separate report contact email and private claim explanations. The campus and starter item pictures are generated demonstration imagery, not real lost property. Each new report uses a shared fictional demo reporter because there is no student login. Andy will independently test the implemented database and app, then add the ER diagram, sample queries, and additional QA evidence.
>>>>>>> origin/work/unified-site

## Progress

**Unified Phase 1 prototype:** the Flask UI, project pages, public SQLite-backed report and claim flow, protected claim review, explainable possible matches, responsive pages, and integration tests are implemented. Real student data and production-grade account management remain outside this classroom demonstration.

AI assistance was used for design, implementation, and test drafting. Alexander remains responsible for reviewing the application and validating the work before release.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
