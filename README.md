# FindIt SDSU — application development milestone

This branch contains an earlier Flask/SQLite implementation of FindIt SDSU, including persistent lost/found reports, item photographs, keyword search, deterministic match suggestions, and private ownership claims.

**Current product:** [Live website](https://finditsdsu.pythonanywhere.com/) · [Current application source](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site)

The code here is retained as an application-development milestone. The deployed `work/unified-site` branch adds public-access safeguards, protected claim review, project pages, and later database migrations. **Do not deploy this older review interface as a public claims service.**

## Features in this branch

- Lost and found reporting with descriptions, campus locations, categories, structured item characteristics, and photos.
- Searchable item listings and individual detail pages.
- Explainable possible matches between compatible lost/found reports.
- Claim creation, review workflow, and SQLite-backed persistence.
- Database migrations and automated functional/database checks.

## Technology and layout

**Python 3.12, Flask, SQLite, Jinja, HTML, CSS, JavaScript and Pillow.**

| Path | Contents |
| --- | --- |
| `app/` | Flask routes, templates, matching, photo processing and tests |
| `database/schema.sql` | SQLite tables, indexes, constraints and triggers |
| `database/migrations/` | Database upgrade scripts |
| `docs/database.md` | Implemented database model |
| `docs/database-evaluation.md` | Synthetic data/query evaluation |
| `run.py` | Local application entry point |

## Run locally

```bash
git clone https://github.com/DellyCodez/FindIt-SDSU.git
cd FindIt-SDSU
git switch work/app
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

Open http://127.0.0.1:5000/. Use fictional item reports and claimant details. The SQLite file and processed uploaded images are stored locally in ignored directories. Do not commit databases, uploads, credentials or real student contact information.

## Testing

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m database.evaluate
```

The evaluation uses a separate synthetic dataset. See the [current application branch](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) for the deployed product, updated requirements and security boundaries.

## Contributors

- **Alexander Hills:** Application development, database integration and deployment.
- **Andy Thai:** Database modeling, SQL verification and testing.
- **Samuel Shadi:** Documentation and presentation.

*Independent CS 514 student prototype; not an official SDSU service.*
