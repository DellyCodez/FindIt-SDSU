# Alexander Hills — Phase 1 contribution record

**Project:** FindIt SDSU (CS 514)  
**Primary role:** Application development, database integration, website integration, deployment, and final product verification  
**Working branches:** `work/app` (initial application), `work/unified-site` (deployed unified product)  
**Live demo:** https://finditsdsu.pythonanywhere.com/  
**Current application source:** https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site

## Scope of work

Alexander coordinated and directed the implementation and integration of the working FindIt SDSU application, including:

- A Flask/Jinja website combining a product-facing homepage, Browse, How It Works, About, Blog, and Resources pages with the working lost-and-found application.
- Public lost and found item submission, including structured item type, brand, model, color, location, date, descriptive details, and optional photo uploads.
- SQLite-backed item listings, keyword search, report-type and category/location filtering, and item detail pages.
- Explainable possible-match suggestions for compatible lost/found reports using structured item attributes and public clues.
- A private-claim workflow with password-protected administrative review, transactional integrity checks, and approval/return status updates.
- Integration of schema migrations, upload handling, validations, CSRF protection, and public-form submission rate limits.
- Publishing the Flask application to PythonAnywhere and manually confirming the public URL loads in an incognito browser.

## Technical evidence

| Area | Files or evidence |
| --- | --- |
| Flask routes, public forms, and restricted administration | [`app/__init__.py`](../app/__init__.py) |
| SQLite access, report search, photos, claims, and moderation | [`app/storage.py`](../app/storage.py) |
| Matching logic and validation | [`app/matching.py`](../app/matching.py), [database design](database.md) |
| Schema, foreign keys, constraints, and migration history | [`database/schema.sql`](../database/schema.sql), [`database/migrations/`](../database/migrations/) |
| Consumer-facing experience and responsive styling | [`app/templates/`](../app/templates/), [`app/static/styles.css`](../app/static/styles.css) |
| Automated functional checks | [`app/test_web.py`](../app/test_web.py), [`app/test_photos.py`](../app/test_photos.py), [`app/test_matching.py`](../app/test_matching.py), [`app/test_stage2_stage3.py`](../app/test_stage2_stage3.py) |
| SQLite benchmark and query evidence on synthetic data | [database evaluation](database-evaluation.md) |
| Hosted deployment and operational instructions | [PythonAnywhere deployment guide](pythonanywhere.md) |
| Final integrated implementation commit | [`18096ae02e6f6d736874568dbf2fd1fae0f81af1`](https://github.com/DellyCodez/FindIt-SDSU/commit/18096ae02e6f6d736874568dbf2fd1fae0f81af1) |

## Verification and limits

The final development handoff reported **23 automated tests passing** and a browser workflow covering report submission, photo upload, search, possible matching, claim submission, and protected approval. The separate synthetic database evaluation records **4,812 fictional reports** and **zero foreign-key violations** in its test database; this is not a claim about real users or real-world matching accuracy.

Alexander performed the existing PythonAnywhere deployment update and confirmed that the public site loads in a private/incognito browser window. This alone is not evidence that every production form was manually retested after deployment; the team should complete a final production smoke test before presenting.

## Division of responsibilities

- **Alexander Hills:** Application and database integration, unified product site, deployment, and product demonstration.
- **Andy Thai:** Database diagram, independent SQL verification, data integrity testing, and quality-assurance evidence.
- **Samueel Shadi:** Presentation, technical documentation, explanatory resources, and final team presentation materials.

The team's full deliverables should include the actual ER diagram, test evidence, and presentation/report materials supplied by the respective collaborators. This record documents Alexander's scope and is not a substitute for each student's confidential teammate evaluation.

## AI assistance

AI coding assistants supported implementation, visual design iteration, and automated test drafting. Alexander directed the requirements and integration, checked the results, managed the GitHub workflow, and performed deployment. This record does **not** claim every code line was manually authored without AI assistance.
