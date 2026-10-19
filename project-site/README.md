# Original FindIt SDSU project site

This directory contains the original static information site used during early Phase 1 development. It includes project overview, About, product, blog, and resources pages, along with captured demo imagery.

**The current product is the Flask/SQLite application, hosted at https://finditsdsu.pythonanywhere.com/.** Its source is maintained on [`work/unified-site`](https://github.com/DellyCodez/FindIt-SDSU/tree/work/unified-site).

## Preview the static site

From the repository root:

```bash
python3 -m http.server 8000
```

Open http://localhost:8000/project-site/. These HTML pages are informational only: they do not run the database, accept live item reports, or process claims. The screenshots use fictional demonstration data.
