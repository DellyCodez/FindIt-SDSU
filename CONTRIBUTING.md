# Contributing to FindIt SDSU

This repository is maintained by a small student team working toward an assessed prototype. Keep changes easy to review and make sure the application remains demonstrable.

## How we work

1. Confirm the task in a GitHub issue. Keep one person accountable for delivery, but involve reviewers early.
2. Create a branch from the current `main`. Use names such as `feature/item-reporting`, `database/schema`, `test/claim-workflow` or `docs/technical-report`.
3. Keep changes focused. Do not modify another teammate's files without coordinating in Discord.
4. Commit work with specific messages: `Add category and location foreign keys` is better than `update`.
5. Open a pull request and include a concise summary, what was tested, screenshots if the interface changed, and any limitations.
6. Ask another teammate to review. Resolve feedback before merging whenever the schedule permits.
7. Update instructions and test evidence when behavior changes.

## Ownership and handoffs

- Alexander: application implementation, integration, local demo.
- Andy: SQL schema and sample data, ER diagram, database/feature tests.
- Samuel: project website content, technical report, slides, documentation and submission checks.

A design choice that affects more than one workstream must be agreed upon first. **In particular, agree on `docs/database-contract.md` before implementing database-backed routes.**

## Definition of done

A feature is complete when it runs, persists the expected data, handles invalid input, is manually checked, has tests appropriate to its risk, and can be explained by its contributor. Only count verified functionality in the README and slides.

## Commit hygiene and data protection

Do not commit `.env` files, secrets, downloaded Canvas materials, real student records, local SQLite databases, cached files, or images you do not have permission to distribute. Keep sample data clearly fictional. Never paste user credentials into an issue or PR.

## AI-assisted work

The course permits limited AI assistance provided it is disclosed and the team can defend the work. Describe the task, tool, what was generated, how it was modified, and what you tested in `docs/ai-use-log.md`. Do not invent manual edits, benchmarks or individual contributions. Everyone remains responsible for reviewing their commits.

## University identity

This is an independent student project. Avoid language, logos or screenshots that imply an SDSU endorsement, official connection or production launch.
