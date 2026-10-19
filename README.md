# FindIt SDSU — database and application QA

This branch records the team's independent database tests and continuous-integration checks for the FindIt SDSU Flask and SQLite prototype.

**Current application:** [Live website](https://finditsdsu.pythonanywhere.com/) · [Production-oriented source](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) · [GitHub Actions](https://github.com/DellyCodez/FindIt-SDSU/actions)

## What was verified

The automated checks exercise the database schema and application behavior, including:

- Foreign-key relationships and invalid-row rejection.
- Item reporting, persistence, search and filtering.
- Claim creation, reviewer decisions, and duplicate/competing-approval prevention.
- Safe schema migrations, photo metadata, matching logic, and access boundaries.
- SQLite integrity rules and repeatable local test setup.

These checks use fictional or synthetic data; they are not a measurement of real-world lost-property recovery accuracy.

## Run locally

Use Python 3.12:

```bash
git clone https://github.com/DellyCodez/FindIt-SDSU.git
cd FindIt-SDSU
git switch test/database-tests
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

On Windows use `py -3.12 -m venv .venv` and the virtual environment's `.venv\Scripts\python.exe` executable.

To run the isolated synthetic database evaluation:

```bash
.venv/bin/python -m database.evaluate
```

The test workflow is defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml). Review actual GitHub Actions runs for precise counts and results, rather than treating documentation as a substitute for a CI run.

## Relationship to the project

FindIt stores lost/found reports, users, categories, locations, photos, claims and rate-limit attempts in related SQLite tables. Data validation, foreign keys, indexes, triggers and transactional claim approval help preserve consistency. The current schema and implementation details are documented in the [active application branch](https://github.com/DellyCodez/FindIt-SDSU/blob/work/unified-site/docs/database.md).

**Contributors:** Alexander Hills (application and integration), Andy Thai (database design and independent QA), Samuel Shadi (documentation and presentation).

*Independent CS 514 student project; not an official SDSU service.*
