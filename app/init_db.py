"""Initialize the local database without deleting existing reports or claims."""

import argparse
from pathlib import Path
import sqlite3

from .demo_fixtures import CATEGORIES, LOCATIONS, demo_items
from .storage import DEMO_REPORTER_EMAIL, PROJECT_ROOT, connect, database_path


def execute_migration(connection, path):
    """Run each migration statement inside the caller's active transaction."""
    statement = ""
    for line in path.read_text().splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            connection.execute(statement)
            statement = ""
    if statement.strip():
        raise RuntimeError(f"Incomplete migration: {path}")


def initialize_database(path=None):
    path = Path(path or database_path()).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(path)
    try:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )}
        if version not in (0, 1, 2, 3, 4, 5, 6, 7, 8) or (version == 0 and tables):
            raise RuntimeError(f"Refusing to change an unknown database at {path}")
        if version == 0:
            # executescript starts an explicit transaction so schema and seed stay atomic.
            connection.executescript("BEGIN IMMEDIATE;\n" +
                                     (PROJECT_ROOT / "database" / "schema.sql").read_text())
        else:
            connection.execute("BEGIN IMMEDIATE")
            if version == 1:
                migration = PROJECT_ROOT / "database" / "migrations" / "002_match_candidates.sql"
                execute_migration(connection, migration)
            if version <= 2:
                migration = PROJECT_ROOT / "database" / "migrations" / "003_item_photos.sql"
                execute_migration(connection, migration)
            if version <= 3:
                migration = PROJECT_ROOT / "database" / "migrations" / "004_item_attributes.sql"
                execute_migration(connection, migration)
        # The published work/app v4 schema used primary_color and filename.
        # Keep its original columns and data while adding the unified names.
        item_columns = {row[1] for row in connection.execute("PRAGMA table_info(items)")}
        if "color" not in item_columns:
            connection.execute("""ALTER TABLE items ADD COLUMN color TEXT
                CHECK (color IS NULL OR length(trim(color)) BETWEEN 1 AND 30)""")
            if "primary_color" in item_columns:
                connection.execute("""UPDATE items SET color = primary_color
                    WHERE primary_color IS NOT NULL AND length(trim(primary_color)) BETWEEN 1 AND 30""")
        if "contact_email" not in item_columns:
            execute_migration(connection, PROJECT_ROOT / "database" / "migrations" / "005_private_report_contact.sql")
        if "distinguishing_features" not in item_columns:
            execute_migration(connection, PROJECT_ROOT / "database" / "migrations" / "006_distinguishing_features.sql")
        photo_columns = {row[1] for row in connection.execute("PRAGMA table_info(item_photos)")}
        if "filename" in photo_columns and "file_name" not in photo_columns:
            connection.execute("ALTER TABLE item_photos RENAME COLUMN filename TO file_name")
        if "byte_size" in photo_columns and "byte_count" not in photo_columns:
            connection.execute("ALTER TABLE item_photos RENAME COLUMN byte_size TO byte_count")
        if "mime_type" not in photo_columns:
            connection.execute("""ALTER TABLE item_photos ADD COLUMN mime_type TEXT NOT NULL
                DEFAULT 'image/webp' CHECK (mime_type = 'image/webp')""")
        connection.execute("""CREATE INDEX IF NOT EXISTS idx_items_match_type
            ON items(kind, status, category_id, item_type, report_date)""")
        if "submission_attempts" not in tables:
            execute_migration(connection, PROJECT_ROOT / "database" / "migrations" / "007_submission_attempts.sql")
        if "visibility" not in item_columns:
            execute_migration(connection, PROJECT_ROOT / "database" / "migrations" / "008_report_visibility.sql")
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
        connection.execute("PRAGMA user_version = 8")
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
