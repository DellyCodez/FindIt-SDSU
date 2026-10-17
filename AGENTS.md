# FindIt SDSU — temporary AI work instructions

We're building FindIt SDSU for our CS 514 database project. Start by reading `README.md`, `docs/database.md`, and `docs/phase-1.md`.

**Before changing anything:** ask which teammate you're helping and confirm that their branch is checked out. A GitHub connection by itself does not tell you who you're helping or which files you should edit.

| Teammate | Branch | Work |
| --- | --- | --- |
| Alexander | `work/app` | Working website: frontend, Flask backend, item reports, search, claim forms, and integration. Mainly `app/` and application setup files. |
| Andy | `work/database` | SQLite schema, sample data, ER diagram, SQL queries, and tests. Mainly `database/`, `tests/`, and database documentation. |
| Samuel | `work/docs` | Technical report, instructions, presentation materials, and content for the separate Google Sites project page. Mainly documentation files. |

## Keep everyone's work separate

- Work only on the assigned branch. Never push directly to `main`, force-push, or merge other people's changes automatically.
- Stick to the teammate's files. If a change to someone else's work is needed, explain it and ask first.
- Alexander and Andy must agree on actual SQL table/column names and constraints **before** the app depends on them. Do not independently create competing database schemas.
- Keep changes small enough to review. Explain what you changed, what you tested, and what is still unfinished.
- After completing a task, help the teammate commit and push to **their own branch** and open a pull request when they ask.
- Don't delete, restructure, or rewrite the repository just to make it fit a generated template.

## About the project

The first version should let a user report a lost/found item, search reports, see item details, submit a claim for a found item, and review claims in a demo workflow. The database should be relational, using users, items, categories, locations, and claims. A found item must not end up with two approved claims.

Keep the site straightforward and polished, but don't add unnecessary features. Use fictional sample data, protect private claim details, and don't suggest the site is an official SDSU service. Never describe unfinished features as working.

AI use must be disclosed as required by the CS 514 assignment. Everyone should understand and verify the work they submit.

*This file is for coordinating AI tools during development. We can remove it later.*
