# PythonAnywhere deployment — FindIt SDSU

This guide targets the `finditsdsu` account, Python 3.12, and
`https://finditsdsu.pythonanywhere.com`. The public site is a **fictional CS 514
demonstration**, not an official SDSU service. Anyone can browse. Reporting,
claims, and claim review require the presenter password. Do not import real
student data or real claims.

## 1. Install the unified branch

In a PythonAnywhere **Bash console**, run these commands for a fresh checkout:

```bash
cd /home/finditsdsu
git clone --branch work/unified-site https://github.com/DellyCodez/FindIt-SDSU.git FindIt-SDSU
python3.12 -m venv /home/finditsdsu/.virtualenvs/findit
/home/finditsdsu/.virtualenvs/findit/bin/python -m pip install --upgrade pip
/home/finditsdsu/.virtualenvs/findit/bin/python -m pip install -r /home/finditsdsu/FindIt-SDSU/requirements.txt
mkdir -p /home/finditsdsu/private/uploads
chmod 700 /home/finditsdsu/private /home/finditsdsu/private/uploads
```

If `/home/finditsdsu/FindIt-SDSU` already contains this repository, use these
commands in place of `git clone`:

```bash
cd /home/finditsdsu/FindIt-SDSU
git fetch origin work/unified-site
git switch work/unified-site || git switch --track origin/work/unified-site
git pull --ff-only origin work/unified-site
```

The pull command deliberately refuses a non-fast-forward update. Back up the
private database and uploads before any later update.

## 2. Create private secrets and initialize SQLite

Run the interactive setup command. It asks for a **unique password of at least
16 characters** without echoing it, generates a random Flask secret, hashes the
password with scrypt, and writes both to a file outside the Git checkout with
mode 600. It refuses to overwrite an existing file.

```bash
cd /home/finditsdsu/FindIt-SDSU
/home/finditsdsu/.virtualenvs/findit/bin/python deployment/create_private_settings.py
export FINDIT_DB_PATH=/home/finditsdsu/private/findit.sqlite3
/home/finditsdsu/.virtualenvs/findit/bin/python -m app.init_db
```

`app.init_db` migrates existing version 1–5 databases in place to version 6,
including the alternate published v4 photo/color column names. It does not
reset reports or claims. Keep the database and `private/uploads/` together in
backups. Do **not** put the private settings, database, or uploads in Git.

If a private database already exists, back it up **before** running `app.init_db`:

```bash
cp /home/finditsdsu/private/findit.sqlite3 /home/finditsdsu/private/findit.sqlite3.before-update
cp -a /home/finditsdsu/private/uploads /home/finditsdsu/private/uploads.before-update
```

## 3. Configure the Web tab

In PythonAnywhere, create or edit the web app for
`finditsdsu.pythonanywhere.com`. Set:

| Web tab field | Value |
| --- | --- |
| Source code | `/home/finditsdsu/FindIt-SDSU` |
| Working directory | `/home/finditsdsu/FindIt-SDSU` |
| Virtualenv | `/home/finditsdsu/.virtualenvs/findit` |
| Static files URL | `/static/` |
| Static files directory | `/home/finditsdsu/FindIt-SDSU/app/static` |

Copy the tested WSGI entrypoint into the exact Web tab WSGI file:

```bash
cp /home/finditsdsu/FindIt-SDSU/deployment/pythonanywhere_wsgi.py /var/www/finditsdsu_pythonanywhere_com_wsgi.py
```

The WSGI entrypoint loads secrets from
`/home/finditsdsu/.config/findit/settings.json`, sets the production host,
database, and upload directory environment variables, imports the Flask app,
and leaves debug mode disabled. Flask refuses to start in public mode without
both secrets. PythonAnywhere writes application exceptions to its Web tab error
log; check that log if a reload fails.

Click **Reload** in the Web tab. Visit the HTTPS URL and verify the home,
About, Our Product, Blog, Resources, Browse, and item detail pages. Check that
the presenter login appears when opening Report Item, Claim, or Review without
signing in. Sign in and run one fictional report-to-approval journey. Confirm
the database and uploaded photos remain after another reload.

## Updating later

Use `git pull --ff-only origin work/unified-site`, install updated requirements,
back up the private data, run `app.init_db`, copy the WSGI entrypoint if it
changed, and click **Reload**. Never run the development server on a public
interface. The existing GitHub Pages project website on `main` should remain
published until this PythonAnywhere deployment is verified.

## Current limits

This presenter-only gate is appropriate for a fictional classroom demo. It is
not student account management, ownership verification, moderation, or email
delivery. The single presenter password should not be shared widely. Public
uploads and real claims require a separate security and privacy review.
