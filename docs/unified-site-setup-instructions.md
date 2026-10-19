# FindIt SDSU Unified Site Setup

Use the `work/unified-site` branch for the final application.

## Local development

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m app.init_db
.venv/bin/python run.py
```

Open `http://127.0.0.1:5000/`. The local database is `instance/findit.sqlite3`; it is ignored by Git and persists across restarts. Processed WebP uploads are stored in the ignored uploads directory.

For tests:

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m database.evaluate
```

## Demonstration flow

1. Browse and filter fictional reports.
2. Report a fictional lost or found item with up to three photos.
3. Open the item details and review Possible Matches.
4. Submit two fictional claims for a found item.
5. Visit `/admin/login` and sign in with the configured presenter password.
6. Approve one claim and observe that the item becomes Returned and the competing pending claim is rejected.
7. Visit `/admin/items` to demonstrate hiding and restoring a report.
8. Reload the app and confirm persistence.

## Public deployment

Public mode requires `SECRET_KEY` and `PRESENTER_PASSWORD_HASH`. Use the documented PythonAnywhere deployment procedure and fictional data only. The deployed site is an independent student project, not an official SDSU service.
