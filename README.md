# FindIt SDSU

**A campus lost-and-found platform built around searchable reports, explainable matches, and private claim review.**

[**Live application**](https://finditsdsu.pythonanywhere.com/) · [**Application source**](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) · [**Database design**](https://github.com/DellyCodez/FindIt-SDSU/blob/work/unified-site/docs/database.md) · [**Technical report**](https://finditsdsu.pythonanywhere.com/static/docs/phase1-technical-report.pdf)

FindIt SDSU is an independent San Diego State University CS 514 database project. It brings lost and found reports into one searchable application, suggests possible matches using public item details, and lets claimants provide identifying information privately for review.


![FindIt SDSU browse-and-search interface](https://raw.githubusercontent.com/DellyCodez/FindIt-SDSU/work/unified-site/app/static/project/about-browse.webp)

## What it does

- **Report lost or found property:** Add a description, category, campus location, date, distinguishing characteristics, and up to three photos.
- **Browse and filter:** Search listings by keywords and narrow results by report type, category, and location.
- **Explore possible matches:** Compare compatible lost/found reports using readable explanations based on their shared details.
- **Submit private claims:** Send identifying evidence without publishing it on the item listing.
- **Review and resolve:** Authorized administrators can approve or reject claims and moderate public reports. An approved claim marks the found item returned.

**Try the application:** https://finditsdsu.pythonanywhere.com/

## Technology

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, JavaScript, Jinja templates |
| Application | Python 3.12, Flask |
| Database | SQLite |
| Image processing | Pillow, WebP |
| Hosting | PythonAnywhere |
| Testing and collaboration | pytest, GitHub Actions, GitHub |

## Database design

The application uses seven related tables: `users`, `items`, `categories`, `locations`, `item_photos`, `claims`, and `submission_attempts`.

The schema includes primary and foreign keys, field constraints, supporting indexes, and triggers for claim status changes. Claim approval runs in a transaction; a partial unique index prevents multiple approved claims for the same item. Photos are stored as processed files, with their metadata linked to items in SQLite.

The matching feature selects eligible opposite-type reports and scores their public attributes. **A suggested match is not proof of ownership.** See the [implemented schema and query design](https://github.com/DellyCodez/FindIt-SDSU/blob/work/unified-site/docs/database.md) for details.

## Repository guide

| Location | Contents |
| --- | --- |
| [`work/unified-site`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) | **Current Flask application**, SQLite schema, tests, and deployment documentation |
| [`test/database-tests`](https://github.com/DellyCodez/FindIt-SDSU/tree/test/database-tests) | Independent database QA and continuous-integration checks |
| [`work/app`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/app) | Earlier application development milestone |
| [`work/database`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/database) | Initial database-planning branch |
| [`work/docs`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/docs) | Documentation and original project-site work |
| [`project-site/`](project-site/) | Earlier static informational site; **not** the deployed Flask application |

The default `main` branch retains the initial project-site source and course planning documents. For the runnable product and current deployment, use `work/unified-site`.

## Run the application locally

Switch to the application branch and use Python 3.12:

```bash
git clone https://github.com/DellyCodez/FindIt-SDSU.git
cd FindIt-SDSU
git switch work/unified-site
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

Then open http://127.0.0.1:5000/. On Windows, substitute `py -3.12 -m venv .venv` and `.venv\Scripts\python.exe` for the corresponding Python commands.

To run tests:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

The development database and uploaded files are ignored by Git. Use fictional reports and contact information for demonstrations. Details and deployment guidance are maintained in the [application branch README](https://github.com/DellyCodez/FindIt-SDSU/blob/work/unified-site/README.md).

## Contributors

| Member | Focus |
| --- | --- |
| **Alexander Hills** | Application development, SQLite integration, site integration, and deployment |
| **Andy Thai** | Database design, ER diagram, SQL verification, and independent testing |
| **Samuel Shadi** | Technical documentation and presentation |

## Project status

A working Phase 1 prototype has been deployed. Student account verification, notifications, and further moderation and operational safeguards are future work. This is **an independent student project, not an official SDSU service**.
