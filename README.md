# FindIt SDSU

**A simpler way to reconnect people with lost belongings on campus.**

FindIt SDSU is an independent, student-developed lost-and-found application being designed for SDSU's CS 514 Database Theory and Implementation course (Fall 2026). The premise is straightforward: someone who loses an item should have one place to search, and someone who finds an item should have a clear way to report it.

**Current stage:** Phase 1 draft. The application is not yet released or approved for campus use. Features described below are planned until a working implementation and tests are committed.

> **Independent project.** FindIt SDSU is not operated, sponsored, approved, or endorsed by San Diego State University. Any future campus integration would require separate review and permission.

## The product

The Phase 1 prototype is deliberately small enough to build and explain clearly.

| Workflow | Expected result |
| --- | --- |
| Report a lost item | A searchable record is saved with its category, location and description. |
| Report a found item | A searchable found-item record is saved. |
| Search campus reports | Visitors can filter by report type, category and location. |
| Request an item | A claim is linked to a found item and a demo user. |
| Review claims | A demo reviewer can approve or reject a claim; one item cannot be awarded twice. |
| View activity | Counts are calculated from persisted records, not hard-coded UI data. |

Phase 1 uses fictional users and sample reports. We will not collect or publish real student contact details for the classroom demonstration.

## Technology direction

**Proposed stack, subject to the team's database-design sign-off:** Python, Flask, SQLite, server-rendered HTML/CSS and minimal JavaScript. We are keeping the initial build straightforward; the schema and application logic can be evolved for a more robust deployment later.

The application is not yet runnable. Setup and run commands will be added with the first working code milestone. We will not publish placeholder commands as if they had been tested.

## Repository guide

| Location | Purpose |
| --- | --- |
| `docs/product-brief.md` | Problem, users, product direction and boundaries |
| `docs/requirements.md` | Phase 1 features and acceptance criteria |
| `docs/database-contract.md` | Proposed relational model for team review |
| `docs/architecture.md` | Proposed application structure and data flow |
| `docs/testing-plan.md` | Functional and database QA plan |
| `docs/phase-1-checklist.md` | Rubric-aligned submission checklist |
| `docs/website-content.md` | Content plan for the separate project website |
| `docs/technical-report-outline.md` | Technical PDF outline |
| `docs/presentation-plan.md` | Eight-minute presentation plan |
| `docs/ai-use-log.md` | Record of AI assistance and human review |
| `CONTRIBUTING.md` | Branch, PR and collaboration conventions |

The app, database scripts and automated tests will be added in later commits by their respective owners.

## Team

- **Alexander Hills — application engineering and integration.** Owns the app's frontend, backend and local demonstration.
- **Andy Thai — database design and quality assurance.** Owns the schema, ER diagram, seed data, SQL validation and tests.
- **Samuel Shadi — technical writing and presentation coordination.** Owns the documentation package, presentation materials and final deliverables checklist.

Roles are initial responsibilities, not a substitute for shared review. Each contributor is expected to understand the product and provide genuine, traceable work. The course calls for 4–6 team members; approval for a three-person team is **not yet confirmed**.

## Course deliverables

The Phase 1 deliverable hub must be a website (for example Google Sites or another site builder) with the About page, product overview/instructions, links to source code and executable, presentation, blog and technical document. Confidential peer evaluations are submitted in individual Canvas comments, **not** on the website. Separate classmate reviews and replies also apply. See [Phase 1 checklist](docs/phase-1-checklist.md).

## Working principles

- Make the database central to the application and show real relationships, joins, constraints and transactions.
- Use clear, accessible UI and realistic sample content rather than decorative dashboards with fabricated metrics.
- Never present planned features, benchmarks, campus partnerships or security controls as completed.
- Document AI assistance as required by the course; review and modify generated work before submission.
- Avoid real personal data, API keys, passwords and local database files in commits.

## Project status

**Planning and repository setup in progress.** The team will update this section as the application, test evidence, deployment link and technical report become available.
