# PythonAnywhere deployment — FindIt SDSU

This guide targets the `finditsdsu` account, Python 3.12, and
`https://finditsdsu.pythonanywhere.com`. The site is an independent CS 514
prototype, not an official SDSU service. Anyone can browse, report, and claim.
Only the admin claim-review area requires the presenter password. Use fictional
data until moderation and operational privacy controls are established.

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

`app.init_db` migrates existing version 1–7 databases in place to version 8,
including the alternate published v4 photo/color column names. It does not
reset reports or claims. Keep the database and `private/uploads/` together in
backups. Do **not** put the private settings, database, or uploads in Git.

If a private database already exists, use the SQLite backup procedure in
**Updating later** below before running `app.init_db`.

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
About, How It Works, Journal, Resources, Browse, and item detail pages. Post one
fictional report with a photo and submit a fictional claim as a signed-out visitor.
Opening `/admin/claims` must redirect to `/admin/login`; sign in there to review
the claim. Check `/admin/items` to hide and restore a fictional report. Confirm
the database and uploaded photos remain after another reload.

## Updating later

In a PythonAnywhere Bash console, back up the private data **before** the pull
or migration. These commands keep the backup outside Git and stop if the branch
cannot advance cleanly:

```bash
set -euo pipefail
cd /home/finditsdsu/FindIt-SDSU
test "$(git branch --show-current)" = work/unified-site
test -z "$(git status --porcelain)"
stamp=$(date -u +%Y%m%d-%H%M%S)
export FINDIT_BACKUP_DIR=/home/finditsdsu/private/backups/$stamp
mkdir -p "$FINDIT_BACKUP_DIR"
git rev-parse HEAD > "$FINDIT_BACKUP_DIR/commit"
/home/finditsdsu/.virtualenvs/findit/bin/python - <<'PY'
import os, sqlite3
source = sqlite3.connect('/home/finditsdsu/private/findit.sqlite3')
target = sqlite3.connect(os.path.join(os.environ['FINDIT_BACKUP_DIR'], 'findit.sqlite3'))
with target:
    source.backup(target)
target.close()
source.close()
PY
cp -a /home/finditsdsu/private/uploads "$FINDIT_BACKUP_DIR/uploads"
git fetch origin work/unified-site
git merge --ff-only FETCH_HEAD
/home/finditsdsu/.virtualenvs/findit/bin/python -m pip install -r requirements.txt
export FINDIT_DB_PATH=/home/finditsdsu/private/findit.sqlite3
/home/finditsdsu/.virtualenvs/findit/bin/python -m app.init_db
cp deployment/pythonanywhere_wsgi.py /var/www/finditsdsu_pythonanywhere_com_wsgi.py
```

Click **Reload** in PythonAnywhere's Web tab and run the signed-out and admin
checks above. Never run the development server on a public interface. The
existing GitHub Pages project website on `main` stays unchanged.

If the reload fails, open the Web tab **Error log** or run
`tail -n 100 /var/log/finditsdsu.pythonanywhere.com.error.log` in a Bash console.
Keep the backup path printed in your console session. To recover from a failed
migration, stop the web app in the Web tab and run the following in the **same
console** with `$FINDIT_BACKUP_DIR` still set:

```bash
cd /home/finditsdsu/FindIt-SDSU
cp "$FINDIT_BACKUP_DIR/findit.sqlite3" /home/finditsdsu/private/findit.sqlite3
cp -a "$FINDIT_BACKUP_DIR/uploads/." /home/finditsdsu/private/uploads/
git switch --detach "$(cat "$FINDIT_BACKUP_DIR/commit")"
```

Reload the web app after restoring. This does not change remote history; switch
back to `work/unified-site` after the issue is fixed. Do not restore a backup
over a running app that might still be accepting submissions.

## Current limits

The single admin password protects claim review; it is not student account
management. Public forms have CSRF, upload validation, a honeypot, and shared
SQLite rate limits. There is no prepublication approval queue, ownership verification,
or email delivery. Public reports appear immediately; administrators can hide
inappropriate content after submission. Real student use needs active moderation
and a privacy review. Protect the private settings,
database, backups, and uploads with filesystem permissions and access policy.
