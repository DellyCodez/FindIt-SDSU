# Architecture — draft

## Proposed Phase 1 deployment

A local Flask application serves HTML, CSS and lightweight JavaScript. HTTP requests hit Flask routes; routes validate input and query a local SQLite database using parameterized statements or a small data-access layer. The repository includes repeatable schema/seed scripts and tests.

```text
Browser
  └── Flask routes + templates
       ├── Report / browse / search / details
       ├── Claim submission
       ├── Demo claim review
       └── Dashboard aggregates
             └── Data-access functions / SQL
                    └── SQLite database
```

**Not implemented yet.** This is the architectural target, not a diagram of running code.

## Planned repository layout

```text
FindIt-SDSU/
  app/                 # Flask app, views, templates, static assets (Alexander)
  database/            # Schema, seeded fictional dataset, migrations (Andy)
  tests/               # Unit and integration tests (Andy; reviewed by Alexander)
  docs/                # Product, database, QA, report and presentation work
  README.md
  requirements.txt     # Added when dependencies are selected
```

The exact internal code organization will follow the first implementation milestone; avoid prematurely creating unused framework directories.

## System boundaries

- Local database is for classroom demonstration only.
- The project submission website is a separate, publishable website that links to actual artifacts.
- A localhost URL does not work for classmates outside the demonstration machine.
- A future public product would require hosting, authentication, authorization, logging, moderation, privacy review and institutional approval.

## Critical integration contract

1. Andy drafts and commits the schema and fictional seed data.
2. Alexander implements routes against reviewed columns and constraints.
3. Andy tests happy-path, validation failures, duplicate claims, and persistence.
4. Samuel documents only workflows that can be demonstrated.
5. Changes affecting the schema require an explicit check with both Alexander and Andy.

## Tradeoffs

SQLite offers straightforward local setup, relational constraints and transactions for the initial demo. It is **not** a commitment to a production architecture. Document concurrency limitations and migration considerations if the project progresses toward institutional use.
