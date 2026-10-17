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

## Progress

**Phase 1 — getting started.** The database and website are being built. Setup instructions and screenshots will be added once there's a working version to run.

Our [Phase 1 checklist](docs/phase-1.md) covers the course deliverables.

---
