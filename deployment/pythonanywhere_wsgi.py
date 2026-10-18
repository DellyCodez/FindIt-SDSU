"""Copy this file to /var/www/finditsdsu_pythonanywhere_com_wsgi.py."""

import json
import logging
import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(os.environ.get("FINDIT_PROJECT_ROOT", "/home/finditsdsu/FindIt-SDSU"))
SETTINGS_PATH = Path(os.environ.get("FINDIT_SETTINGS_PATH", "/home/finditsdsu/.config/findit/settings.json"))
PRIVATE_ROOT = Path(os.environ.get("FINDIT_PRIVATE_ROOT", "/home/finditsdsu/private"))

settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
for name in ("SECRET_KEY", "PRESENTER_PASSWORD_HASH"):
    if not settings.get(name):
        raise RuntimeError(f"Missing {name} in the private settings file")
    os.environ[name] = settings[name]
os.environ["FINDIT_PUBLIC"] = "1"
os.environ.setdefault("FINDIT_ALLOWED_HOSTS", "finditsdsu.pythonanywhere.com")
os.environ["FINDIT_DB_PATH"] = str(PRIVATE_ROOT / "findit.sqlite3")
os.environ["FINDIT_UPLOAD_DIR"] = str(PRIVATE_ROOT / "uploads")

sys.path.insert(0, str(PROJECT_ROOT))
logging.basicConfig(level=logging.WARNING)
from wsgi import application  # noqa: E402

application.debug = False
