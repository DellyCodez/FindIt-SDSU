# FindIt SDSU — instructions for AI helpers (temporary)

We're three CS 514 students building **FindIt SDSU**, a campus lost-and-found website. We want an actual working database project, not a collection of mockups. Keep your work simple, clear, and testable.

**Read these files first, in this order:**
1. `README.md` — what the project does.
2. `docs/database.md` — the draft tables and relationships.
3. `docs/phase-1.md` — what the professor requires for Phase 1.
4. The current files in your assigned branch — check whether work already exists before generating anything.

The full professor assignment PDF is not stored in this repository. Ask your teammate for it before finalizing course deliverables. If the README and assignment disagree, confirm the requirement with your teammate; don't invent an answer.

## Identify who you're helping

Ask **"Are you Alexander, Andy, or Samuel?"** if that isn't already clear. Confirm the correct repo and branch before making edits. If you're reading through a GitHub connector that cannot select branches, commit, or run code, say what is and isn't possible rather than assuming.

| Person | Branch | Owns |
| --- | --- | --- |
| Alexander | `work/app` | Flask frontend/backend, the authoritative SQLite schema, database access and integration |
| Andy | `work/database` | QA/test ownership; assists with fictional seed data, ER diagram, SQL verification and bug reports |
| Samuel | `work/docs` | Separate project website, technical report, instructions, presentation |

## Andy — QA / database testing and support

**New assignment:** Alexander is now writing **`database/schema.sql`** and the Flask SQLite integration. Andy is **not** responsible for creating a parallel or replacement schema. His role is to prove that the application and its database work, and to help with the supporting database deliverables.

**Start now (even if SQLite is unfinished):**
- Review the Flask proof of concept already committed on `work/app`. Ask Alexander for permission to sync that code into your **own** QA branch when needed. Do not push changes to `work/app` or `main`.
- Write a simple Phase 1 manual test plan/checklist in `docs/qa-checklist.md`, covering browsing, searching/filtering, lost/found reports, claims, reviewer approval/rejection, incorrect inputs, and mobile layouts.
- Run the app and its existing web tests locally if your environment supports it. Record **actual** results (pass/fail, commands and errors) in `docs/qa-results.md`; report reproducible bugs to Alexander.
- Once Alexander's `database/schema.sql` is available, review the **actual** tables, PK/FK relationships, constraints and normalization; make an ER diagram under `docs/` that matches the implemented schema.
- Prepare `database/seed.sql` or an equivalent fixture script with fictional sample users/items/claims **after** the schema is final. Coordinate field names with Alexander; do not change the schema to make the seed data fit.
- Provide representative SQL queries demonstrating JOIN, COUNT/GROUP BY and filtering, with their verified results. Put them in `database/sample_queries.sql` (or an equivalent document).
- Add tests in `tests/` for invalid foreign keys, required fields/statuses, record persistence across app restarts, and two competing claims for the same item (only one can be approved). Use the current schema and the app's real data access layer; don't test a different database model.
- Perform an end-to-end check on desktop/mobile and give Samuel accurate screenshots/test observations when asked. Verify a clean setup from README.

**Done means:** Tests and manual checks actually ran; failures and reproduction steps are documented; ER diagram, queries and seed data reflect Alexander's schema; important bugs are communicated to Alexander. Never claim a test passed without running it.

**Boundaries:** Use `work/database`. Don't create or edit `database/schema.sql`, `app/` Flask routes/templates, or `run.py` without Alexander's agreement. When tests need application code, arrange to bring the committed `work/app` changes into your own branch first (ask before merging). Keep your own QA/seed/diagram changes separate and create a PR for review.

## Samuel — project website, documentation, presentation

**Start here:** Read `docs/phase-1.md`, ask for the professor's PDF, and draft the deliverables before waiting for the app. You're preparing the materials that present the project, not building its Flask interface.

**Your work:**
- Set up the **separate project website** using Google Sites or another permitted site builder. It needs an About section (project purpose, team, problem), product overview and instructions, and links to real deliverables. `localhost` is not a public website link.
- Prepare a technical document for PDF export. Include the problem, actual database design and ER diagram from Andy, SQL concepts used, application implementation from Alexander, screenshots from the running app, test evidence, setup/user instructions, and limitations.
- Prepare an **8-minute group presentation** plus roughly 2 minutes for questions. Cover the problem, database design, demo, what works, and next steps. Make space for everyone to speak.
- Create the blog section on the project website, but **each member must write their own paragraph**. Ask for their text; don't fabricate personal contributions.
- Check that the GitHub, document, presentation and demo links work, and that the actual source/setup instructions match the tested version.

**Done means:** The website is published and accessible, the PDF/slides are linked, actual screenshots and claims are accurate, each person has contributed their own writing, and the team has rehearsed. If you cannot publish to Google Sites or Slides from your AI tool, prepare the content and clearly tell Samuel which steps he needs to do.

**Important:** Confidential teammate evaluations go separately in each student's Canvas submission comments, not on the public website. The project also has a separate discussion requirement involving classmate reviews and replies.

## Alexander — application and SQLite development

**App build brief:** Read [`docs/app-build.md`](docs/app-build.md) for the approved visual design and latest app status. The Flask proof-of-concept implementation is already committed on `work/app`; **extend that existing app, don't rebuild it**.

**New assignment:** Alexander owns both the working Flask application and the **single authoritative SQLite schema and integration**. Andy provides testing and supporting database deliverables.

**Your work:**
- Preserve and refine the existing homepage, browse/search, report, item details, claims and clearly marked demo-only review pages.
- Create `database/schema.sql` on `work/app`: normalize the planned users, categories, locations, items and claims; include primary/foreign keys, NOT NULL/CHECK constraints, useful indexes, and a database-level rule preventing two approved claims on one found item.
- Decide exact columns based on current web forms/routes; write these down in `docs/database.md` **after** implementing them. Avoid unnecessarily breaking the existing `DemoStore` interface.
- Implement a small SQLite data layer and replace the process-local `DemoStore` for normal runs, preserving working functionality. Initialize the local SQLite database through an explicit repeatable command/script, never by committing a .db file.
- Use `PRAGMA foreign_keys = ON` on every database connection. Use atomic transactions for approvals; protect private claim evidence from public pages.
- Keep the demo-only reviewer restricted to local demonstration until real authentication exists. Use fictional names and email addresses.
- Add integration tests for report → search → claim → approval, persistence after restart and second-approval rejection. Let Andy independently review/test them and contribute further tests/seed data.
- Give Samuel actual screenshots, setup instructions, database design details and any limitations.

**Done means:** The app runs from clean setup with SQLite persistence, both the UI and data integrity checks work, and Andy has reproducible test results. Work only on `work/app`, not `main`.

## Rules for everybody's AI

- **Never push directly to `main`**, force-push, delete someone else's work, or merge a pull request without the student's approval. Work only in the assigned branch. Suggest changes rather than taking destructive actions.
- Avoid creating a second app, a second database schema, or overwriting existing documents. Ask when responsibilities overlap.
- Make code and documents understandable to a student who needs to explain them in class. No fake features, fake data presented as real campus records, imaginary benchmarks, or university endorsement.
- Use fictional data. Don't commit passwords, private student information, local databases or API keys.
- The professor requires **disclosure of AI assistance**. Help the student describe what AI helped with, what they personally checked/changed, and what actually works. Don't misrepresent authorship.
- After a work session, give the teammate a short summary: **files changed, tests run/results, remaining work, and what needs another teammate's input**. Only call something complete when you've verified it.

*Remove this file and `CLAUDE.md` when the team no longer needs AI handoff instructions.*
