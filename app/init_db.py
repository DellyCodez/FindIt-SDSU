"""Initialize the local database without deleting existing reports or claims."""

import argparse
from pathlib import Path

from .demo_fixtures import CATEGORIES, LOCATIONS, demo_items
from .storage import DEMO_REPORTER_EMAIL, PROJECT_ROOT, connect, database_path


def initialize_database(path=None):
    path = Path(path or database_path()).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(path)
    try:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )}
        if version not in (0, 1, 2, 3, 4) or (version == 0 and tables):
            raise RuntimeError(f"Refusing to change an unknown database at {path}")
        if version == 0:
            # executescript starts an explicit transaction so schema and seed stay atomic.
            connection.executescript("BEGIN IMMEDIATE;\n" +
                                     (PROJECT_ROOT / "database" / "schema.sql").read_text())
        else:
            connection.execute("BEGIN IMMEDIATE")
            if version == 1:
                migration = PROJECT_ROOT / "database" / "migrations" / "002_match_candidates.sql"
                connection.execute(migration.read_text())
            if version in (1, 2):
                migration = PROJECT_ROOT / "database" / "migrations" / "003_item_photos.sql"
                # Split this simple DDL file so the surrounding transaction remains active.
                for statement in migration.read_text().split(";"):
                    if statement.strip():
                        connection.execute(statement)
            if version in (1, 2, 3):
                migration = PROJECT_ROOT / "database" / "migrations" / "004_item_attributes.sql"
                for statement in migration.read_text().split(";"):
                    if statement.strip():
                        connection.execute(statement)
        connection.execute("INSERT OR IGNORE INTO users(name, email) VALUES (?, ?)",
                           ("Demo Reporter", DEMO_REPORTER_EMAIL))
        for category in CATEGORIES:
            connection.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (category,))
        for location in LOCATIONS:
            connection.execute("INSERT OR IGNORE INTO locations(name) VALUES (?)", (location,))
        if connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0:
            for item in demo_items():
                connection.execute("""
                    INSERT INTO items
                        (reporter_id, category_id, location_id, title, description,
                         kind, status, report_date, image_key)
                    VALUES (
                        (SELECT id FROM users WHERE email = ?),
                        (SELECT id FROM categories WHERE name = ?),
                        (SELECT id FROM locations WHERE name = ?),
                        ?, ?, ?, ?, ?, ?
                    )
                """, (DEMO_REPORTER_EMAIL, item["category"], item["location"],
                      item["title"], item["description"], item["kind"], "Open",
                      item["report_date"], item["image"]))
        connection.execute("PRAGMA user_version = 4")
        connection.commit()
        return path
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description="Initialize FindIt SDSU's SQLite demo database")
    parser.add_argument("--database", type=Path, help="Optional database path for a fresh demo")
    args = parser.parse_args()
    path = initialize_database(args.database)
    print(f"Database ready: {path}")


if __name__ == "__main__":
    main()
