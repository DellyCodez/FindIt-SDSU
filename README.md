# FindIt SDSU

**A searchable campus lost-and-found application with explainable matches and a private claim-review workflow.**

[Live website](https://finditsdsu.pythonanywhere.com/) · [Project overview](https://finditsdsu.pythonanywhere.com/about) · [Technical report](https://finditsdsu.pythonanywhere.com/static/docs/phase1-technical-report.pdf) · [Independent database QA](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests)

FindIt SDSU brings lost and found reports together in a structured database rather than leaving details scattered among group chats and posts. Students can search shared reports, compare possible matches, and submit private identifying information for administrative review. This is an independent CS 514 student prototype, not an official San Diego State University service.

## Features

- **Item reporting:** Public lost/found report forms capture category, campus location, date, descriptive attributes, and up to three photos.
- **Search and discovery:** Browse available reports and filter by keywords, kind, category, and location.
- **Possible Matches:** A deterministic, explainable matching process compares eligible lost/found records using public attributes and time windows.
- **Private claims:** Claim evidence and contact information are kept out of public item listings.
- **Protected review:** An authenticated administrator reviews ownership claims, approves or rejects submissions, and can hide or restore item listings.
- **Reliable persistence:** Submitted items, claims, and metadata are stored in SQLite; processed photos are stored separately as WebP files.

## Tech stack

| Component | Implementation |
| --- | --- |
| Web frontend | HTML, CSS, JavaScript, Jinja |
| Application server | Python 3.12 and Flask |
| Database | SQLite, migration scripts, indexes, constraints, triggers |
| Image pipeline | Pillow (validation, orientation, WebP conversion) |
| Deployment | PythonAnywhere with WSGI |
| Tests | pytest, browser checks, independent GitHub Actions QA |

## Database design

The implemented relational schema has **seven tables**: `users`, `items`, `categories`, `locations`, `item_photos`, `claims`, and `submission_attempts`.

Foreign keys associate each report with its reporter, category, and location, while photos and claims reference their items. Supporting constraints and indexes preserve data integrity and make common queries efficient. A partial unique index permits at most one approved claim per item. Claim approval uses a transaction and triggers to mark the item returned and reject competing pending claims.

Possible-match queries select eligible opposite-type reports in a bounded date window. Application logic then ranks candidates from compatible public details. Suggestions are leads to investigate, not automatic ownership decisions.

Read [the detailed database documentation](docs/database.md), [schema](database/schema.sql), and [evaluation notes](docs/database-evaluation.md).

## Local setup

**Prerequisites:** Python 3.12 and a terminal. Use fictional data for local or public demonstrations.

### macOS / Linux

```bash
git clone https://github.com/DellyCodez/FindIt-SDSU.git
cd FindIt-SDSU
git switch work/unified-site
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

### Windows PowerShell

```powershell
git clone https://github.com/DellyCodez/FindIt-SDSU.git
cd FindIt-SDSU
git switch work/unified-site
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m app.init_db
.venv\Scripts\python.exe run.py
```

Open **http://127.0.0.1:5000/**.

The initializer creates `instance/findit.sqlite3` if needed, seeds fictional starter reports only when there are no items, and applies supported migrations without discarding existing submissions. Use `FINDIT_DB_PATH` to choose another SQLite database location. Processed images live in `instance/uploads/` unless configured otherwise; back up the database and uploads together.

**Deployment:** Public configuration requires a secret key and password hash for protected administrative access. Configuration values, local databases, and uploaded files must not be committed. Follow [PythonAnywhere setup](docs/pythonanywhere.md) for the actual deployment boundaries and environment variables. The public report/claim flows still require moderation and are intended for demonstration, not campus-wide operation.

## Run tests and reproduce the database evaluation

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m database.evaluate
```

The test suite covers validation, reports and photos, persistence and migrations, matching, private claims, administrative review, and database integrity. The evaluation script uses synthetic records in a separate temporary database; its results are not measured production accuracy. Independent QA and workflow history are available on the [database-testing branch](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests).

## Product walkthrough

1. Open the [live browse page](https://finditsdsu.pythonanywhere.com/items) and search or filter the fictional reports.
2. Report a lost or found item and include distinguishing information to help identify possible matches.
3. Inspect an item's public details and any suggested matches.
4. Submit a private claim for a found item with identifying evidence.
5. An authorized reviewer checks submitted evidence and can approve or reject it. An approved item becomes Returned.

The public experience does not currently include verified student accounts, email notifications, automated ownership verification, or SDSU identity integration.

## Project structure

```text
app/                  Flask routes, templates, styles, matching and photo logic
database/             Schema, incremental migrations and evaluation utility
deployment/           PythonAnywhere WSGI and private setup helpers
docs/                 Database design, deployment and verification notes
app/test_*.py         Application and database integration checks
requirements*.txt     Runtime and testing dependencies
run.py                Local Flask entry point
```

## Team

| Contributor | Responsibility |
| --- | --- |
| **Alexander Hills** | Flask application, database integration, website design/integration, and deployment |
| **Andy Thai** | Database model, ER diagram, SQL verification, and independent tests |
| **Samuel Shadi** | Technical documentation and presentation |

## Status and next steps

The Phase 1 prototype has a deployed reporting, browsing, matching and claim-review workflow. Future improvements include verified student accounts, notifications, stronger moderation workflows, media storage improvements, and operational monitoring.

**FindIt SDSU is an independently developed classroom prototype, not an official SDSU service.**
