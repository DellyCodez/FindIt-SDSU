"""Interactively create private PythonAnywhere settings outside the repository."""

from getpass import getpass
import json
import os
from pathlib import Path
import secrets

from werkzeug.security import generate_password_hash


def main():
    destination = Path.home() / ".config" / "findit" / "settings.json"
    if destination.exists():
        raise SystemExit(f"Private settings already exist at {destination}; refusing to overwrite them.")
    password = getpass("Choose a unique presenter password (at least 16 characters): ")
    confirm = getpass("Confirm presenter password: ")
    if len(password) < 16 or password != confirm:
        raise SystemExit("Password must be at least 16 characters and the two entries must match.")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(destination.parent, 0o700)
    settings = {"SECRET_KEY": secrets.token_urlsafe(48),
                "PRESENTER_PASSWORD_HASH": generate_password_hash(password, method="scrypt")}
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as output:
        json.dump(settings, output)
        output.write("\n")
    print(f"Private settings created at {destination} (mode 600). Keep this file out of Git.")


if __name__ == "__main__":
    main()
