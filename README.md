# FindIt SDSU — documentation and original project site

This branch preserves the team's Phase 1 documentation, setup notes, and original static informational website.

**Current product:** [Live FindIt SDSU application](https://finditsdsu.pythonanywhere.com/) · [Current source and deployment](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site) · [Technical PDF](https://finditsdsu.pythonanywhere.com/static/docs/phase1-technical-report.pdf)

## What's included

| Path | Purpose |
| --- | --- |
| `project-site/` | Original static project overview, About, Blog, product instructions, and resources |
| `docs/setup-instructions.md` | Earlier local application setup and demonstration |
| `docs/unified-site-setup-instructions.md` | Setup notes for the integrated Flask website |
| `docs/phase-1-final-evidence.md` | Team submission evidence and source references |
| `docs/andy-evidence-review.md` | Review of independent database-testing evidence |
| `docs/phase-1-report-source.md` | Technical-report source notes |

The older static site is not a live lost-and-found database. The deployed Flask application handles reporting, searching, matching, and claim review.

## Preview the original static site

From the repository root:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000/project-site/. For the actual working product, use the hosted app or the `work/unified-site` branch and follow its README.

## Team

- **Alexander Hills:** Application, database integration, product site integration and deployment.
- **Andy Thai:** Database design, ER diagram, SQL testing and QA.
- **Samuel Shadi:** Documentation and presentation.

This documentation branch is retained for the project's contribution history. The maintained implementation is available on `work/unified-site`.

*FindIt SDSU is an independent CS 514 student prototype, not an official SDSU service.*
