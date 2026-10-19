# Final website refinement verification

Verified on `work/unified-site` on October 19, 2026. These results describe the
local running Flask application. PythonAnywhere has not been updated by this
verification session.

## Scope and reconciliation

The checkout advanced from `18096ae` to remote commit `60344ba` before the final
refinements. Existing local template and test changes were saved in a safety
stash and file backups, then reapplied and reconciled. The remote contribution
notes and PDF publication commits are retained. Resources contains one PDF link
and the five existing code/documentation links.

The About page now explains the purpose, reporting/search/matching/claim journey,
and team responsibilities in a responsive editorial layout. Shared typography,
form readability, heading wrapping, and search focus treatment were refined.
The homepage campus image now stays within its own montage quadrant on mobile
and tablet. Samuel Shadi's name is corrected in About, Journal, README, and the
technical report. Journal paragraphs and the AI assistance disclosures remain
intact. No schema, matching, authentication, or dependency changes were made.

## Automated suite

Run from the repository root with the existing development environment:

```bash
.venv/bin/python -m pytest -q
```

Result: **24 passed**. This includes the retained PDF link/response check, report
and claim workflows, validation, CSRF, private admin access, uploads, matching,
moderation, migrations, foreign keys, competing claims, and restart persistence.
The PDF check requires exactly one Resources link and a successful
`application/pdf` response with a PDF header.

## Actual browser checks

Chromium with Playwright against Flask bound to loopback, using an isolated,
ignored SQLite database and fictional submissions:

- Nine public pages at **1440, 768, and 375 pixels**: Home, About, Browse,
  Report, item details, claim form, Journal, How It Works, Resources.
- **27 page checks** returned HTTP 200, with no broken images, horizontal
  overflow, misspelled visible names, or JavaScript errors. Screenshots were
  captured from the running application and visually reviewed.
- The Resources PDF link opened a new tab at all three widths and returned
  HTTP 200 with `application/pdf`.
- Mobile/tablet menu opening and Escape dismissal, keyboard skip-link focus,
  mobile filter expansion, and all **18 unique internal links** encountered in
  the public journey passed. Journal fragment targets resolve.
- Submitted an invalid report, then a fictional lost notebook and a corresponding
  found notebook, each with a real PNG upload processed to WebP. Search and the
  mobile Lost filter found the submitted report; its Possible Matches section
  suggested the found report with item-type and other public explanations.
- Opened the match, checked invalid-claim validation, submitted a fictional claim,
  signed in to the protected reviewer, and approved it. The item became Returned.
  Private report contact, claimant contact, and claim evidence were absent from
  public pages. Review and matching screens were also checked at all three widths.
- After stopping and restarting Flask (which repeats safe initialization), all
  **8 reports, 1 claim, users, photo metadata, and 2 processed photo files** were
  unchanged. The item remained Returned and the reviewer remained protected.
  SQLite `integrity_check` returned `ok`; `foreign_key_check` returned no rows.

Browser artifacts are local review files under ignored
`instance/final-refinement/`; no runtime database, upload, password, or browser
output is included in Git. The deployment's existing data was not accessed.

## Technical report

Single hosted path: `/static/docs/phase1-technical-report.pdf`.

The supplied and remotely published PDFs had the same SHA-256:
`d09c2cb90773c0e4a34a92d692c9dc514d41631ec7d6440b4d44df058deb45d3`.

No editable document source was present. The correction removed the extra letter
from the existing embedded Arial glyph draws on pages 1 and 9, adjusted the
following text positions on those lines, and retained the remaining PDF objects.
This uses the existing fonts rather than overlaying replacement text.

Validation with PyMuPDF and Poppler (local review tools, not app dependencies):

- All **10 pages, 17 clickable links, fonts, and embedded images** retained.
- Entire extracted text equals the original with only the two name corrections.
- The other eight pages render pixel-for-pixel identically at 72 DPI.
- Pixel differences on pages 1 and 9 are confined to the corrected text rows.
  Both corrected pages were rendered at 108 DPI and visually inspected.
- Diagrams, screenshots, technical claims, and AI disclosure retained.

Corrected PDF SHA-256:
`99514d9f2c7c233657fc37ae18376a305df635da7f7d3afdd06c9018a4599585`.

## Review and deployment limits

Browser checks used Chromium, not physical phones or Safari. They validate this
refinement, not ownership verification or a full security audit. The existing
Phase 1 limits described in README and the report still apply. The original
editable report should also receive the corrected name before a later re-export.

Use the **Website refinement only** instructions in
[the PythonAnywhere guide](pythonanywhere.md#website-refinement-only), then click
Reload in the Web tab. That update keeps private SQLite data, uploads, and secrets
outside the checkout and does not run a database migration.
