# FindIt SDSU public project website

This is a separate static presentation site for the CS 514 Phase 1 project. It is not the Flask application and does not accept reports or claims.

## Preview locally

From the repository root, run:

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/project-site/`. All page and asset links are relative, so the same files work when GitHub Pages serves them under `/FindIt-SDSU/`.

## Source and images

Feature descriptions were checked against `work/app` at `6f6321e`. The five screenshots in `assets/` are captures from that local app with fictional demo reports. They show only public-facing report information. The project site does not include the SQLite database, upload directory, or private claim/reviewer screens.

## Before publishing for the course

- Replace each blog placeholder with an original paragraph from Alexander, Andy, and Samuel, respectively.
- Add the finished technical PDF, verified ER diagram, and reviewed presentation slides, then replace the pending labels with real links.
- Review the course PDF and final site copy with the team. Add the required AI assistance disclosure based on what each member actually used and checked.
- Review and merge the website pull request into `main`. The Pages workflow deploys only `project-site/` when that branch receives the site changes. In repository Settings → Pages, select **GitHub Actions** as the source.

The local Flask app is on `work/app`. Its demo reviewer has no production authentication; do not deploy that app as a real claims service.
