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
| Alexander | `work/app` | The actual application: frontend, Flask backend, and integration |
| Andy | `work/database` | SQLite schema, ER diagram, seed data, SQL queries, and tests |
| Samuel | `work/docs` | Separate project website, technical report, instructions, presentation |

## Andy — database and testing

**Start here:** Read `docs/database.md`. Show Alexander your proposed table names, field types and relationships **before** implementing them. Agree on those fields so the web app doesn't build against a different schema.

**Your work:**
- Build `database/schema.sql` for users, categories, locations, items and claims, with primary keys, foreign keys, required fields, sensible status constraints, and indexes when useful.
- Make `database/seed.sql` (or a repeatable seed script) with **fictional** students and lost/found reports. It should work from a fresh database.
- Draw an ER diagram and put it under `docs/` so Samuel can use it in the report.
- Provide a few real SQL queries using JOIN, GROUP BY/COUNT, and filters. Explain what each shows.
- Implement tests under `tests/` for foreign keys, report/claim relationships, and the claim approval rule. In SQLite, enable foreign-key enforcement for each connection. The app and database must prevent two approved claims for the same found item.
- Once Alexander has working pages, test creating items, searching, submitting claims, resolving claims, and checking persistence after refresh/restart. Report steps to reproduce any bug.

**Done means:** The schema and seed data run, the ER diagram matches the tables, tests have actual results, and Alexander has agreed to the schema. Don't claim tests passed unless you ran them. Don't edit application templates or routes without checking with Alexander.

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

## Alexander — application and integration

**App build brief:** Read [`docs/app-build.md`](docs/app-build.md) first. It records the approved UI direction, screens, implementation order, integration boundary, and definition of done. This is the main handoff for Codex on `work/app`.

**Start here:** Read the same project docs, check existing files, then get Andy's agreed SQL schema before writing database-dependent routes.

**Your work:**
- Build a small, polished Flask application with HTML/CSS/JS and SQLite. Keep the setup straightforward and document how to run it.
- Pages/flows: list lost/found reports; create a report; search/filter by type, category and location; view item detail; submit a claim on a found item; review a claim through a clearly marked **demo-only** reviewer page.
- Save and retrieve real database records, handle invalid form inputs, and display useful empty and error states. Don't hardcode counts or pretend demo buttons work.
- Work with Andy on claim approval as a transaction. The same found item must not be awarded twice, and private claim evidence must not show on public item pages.
- Supply Samuel with **real** screenshots, the exact startup steps and a concise explanation of the implemented features.
- Integrate reviewed pull requests and make sure the complete application runs from a fresh setup.

**Done means:** A report can be created, found via search, claimed, and reviewed; changes persist in SQLite; the README tells a teammate how to run the project; tests and demo steps reflect real behavior.

## Rules for everybody's AI

- **Never push directly to `main`**, force-push, delete someone else's work, or merge a pull request without the student's approval. Work only in the assigned branch. Suggest changes rather than taking destructive actions.
- Avoid creating a second app, a second database schema, or overwriting existing documents. Ask when responsibilities overlap.
- Make code and documents understandable to a student who needs to explain them in class. No fake features, fake data presented as real campus records, imaginary benchmarks, or university endorsement.
- Use fictional data. Don't commit passwords, private student information, local databases or API keys.
- The professor requires **disclosure of AI assistance**. Help the student describe what AI helped with, what they personally checked/changed, and what actually works. Don't misrepresent authorship.
- After a work session, give the teammate a short summary: **files changed, tests run/results, remaining work, and what needs another teammate's input**. Only call something complete when you've verified it.

*Remove this file and `CLAUDE.md` when the team no longer needs AI handoff instructions.*
