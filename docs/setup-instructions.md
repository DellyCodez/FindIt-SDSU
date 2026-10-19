# FindIt SDSU Local Setup and Demonstration

This guide describes the verified local classroom demonstration for the `work/app` branch. It is separate from the public PythonAnywhere page and should be used with fictional names, email addresses, and item details only.

## Requirements

- Python 3.12
- A terminal and web browser
- The repository checked out at `work/app`

## Install and initialize

From the repository root on macOS or Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe -m app.init_db
.\\.venv\\Scripts\\python.exe run.py
```

Open `http://127.0.0.1:5000/`. The initializer creates the local SQLite file at `instance/findit.sqlite3` and seeds six fictional starter reports only when the database has no items. Re-running initialization preserves existing records and applies safe migrations. Never commit the `.sqlite3` file.

## Demonstration sequence

1. Browse the fictional reports and use the text search and Lost/Found, category, location, and sort filters.
2. Report a fictional found item. Select the category-specific item type and primary color. Add optional brand, model, distinguishing features, and up to three JPEG, PNG, or WebP photos.
3. Confirm the new report opens and shows its details and any Possible Matches.
4. Open a found item and submit a claim using an invented name, email, and identifying explanation. The identifying explanation remains private to the local reviewer page.
5. Open **Demo reviewer** from the footer or mobile menu. The reviewer is intentionally local-only and unauthenticated. Approve or reject the pending claim.
6. After approval, the item becomes Returned and competing pending claims are rejected. A second approval cannot succeed.
7. Restart the server and reopen the item to demonstrate SQLite persistence.

## Photos and matching

The application accepts 1–3 photos per report, with an 8 MB per-file limit and 25 MB total request limit. Pillow validates and re-encodes uploads as WebP; SQLite stores metadata while files remain in the ignored local upload directory. Possible Matches compare opposite-type open reports using category, item type, date range, color, brand, model, location, and distinctive public details. The score is a similarity heuristic, not proof of ownership.

## Testing and evaluation commands

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m database.evaluate
```

The repository documents a 24-test application run and a separate synthetic database evaluation. Andy's independent QA results and final SQL verification still need to be attached before the Phase 1 package is final.

## Public deployment boundary

The public demonstration page is `https://finditsdsu.pythonanywhere.com/`. The project is a student prototype, not an official SDSU service. The local demo reviewer has no production authentication and should not receive real student data or be treated as a production claims workflow.
