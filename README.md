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

The claim process is the main feature we want to get right. A found item may have more than one claimant, but the system should only allow one approved claim.

## Database

We're planning to use five related tables: `users`, `items`, `categories`, `locations`, and `claims`. This lets us keep reports organized and track who submitted each item and claim.

See [Database design](docs/database.md) for the current plan.

## Tech stack

Our starting plan is **Python (Flask), SQLite, HTML, CSS, and JavaScript**. We're keeping the setup simple so we can focus on the database and a working website. We'll update this section if we change anything.

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

The current app is a **local proof of concept** with fictional reports. It uses an in-memory store while Alexander implements SQLite persistence. Reports, claims, and review decisions work during one server run and **reset when the server restarts**. The demo reviewer page has no production authentication; use invented names and email addresses only.

With Python 3.12, from the repository root (macOS/Linux):

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
```

Open `http://127.0.0.1:5000/` in your browser. Stop the server with Ctrl+C. On Windows PowerShell, use `.venv\Scripts\python` in place of `.venv/bin/python` after creating the virtual environment with `py -3 -m venv .venv`.

To run the web flow checks:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q app/test_web.py
```

Try the demo in this order:

1. Browse the fictional lost and found reports; search by text and filter by report type, category, or location.
2. Report a **found** item with invented details. The new report opens automatically.
3. Claim the found item with an invented name, email, and identifying detail. The detail is private to the local reviewer screen.
4. Use **Demo reviewer** in the footer (or mobile menu) to approve or reject the claim. Approval marks the item returned and prevents a second approval.

The app has no login, uploads, email, or public deployment workflow. The campus and item pictures are generated demonstration imagery, not real lost property. Database persistence is next on Alexander's branch; Andy will test the database and app after integration.

## Progress

**Phase 1 proof of concept:** the Flask UI, in-memory demo flow, responsive pages, and route tests are implemented. SQLite integration remains pending the agreed schema.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
