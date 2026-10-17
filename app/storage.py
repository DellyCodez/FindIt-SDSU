"""Small SQLite data layer matching the existing Flask page interface."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "instance" / "findit.sqlite3"
DEMO_REPORTER_EMAIL = "reporter@example.test"


def database_path():
    return Path(os.environ.get("FINDIT_DB_PATH", DEFAULT_DATABASE)).expanduser().resolve()


def connect(path):
    connection = sqlite3.connect(path, timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


class SQLiteStore:
    def __init__(self, path=None):
        self.path = Path(path or database_path()).resolve()
        if not self.path.is_file():
            raise RuntimeError(f"Database missing at {self.path}. Run: python -m app.init_db")
        with self.connection() as connection:
            if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
                raise RuntimeError("Database schema version is unknown. Run the documented setup.")

    @contextmanager
    def connection(self):
        connection = connect(self.path)
        try:
            yield connection
        finally:
            connection.close()

    def list_categories(self):
        with self.connection() as connection:
            return [row[0] for row in connection.execute("SELECT name FROM categories ORDER BY id")]

    def list_locations(self):
        with self.connection() as connection:
            return [row[0] for row in connection.execute("SELECT name FROM locations ORDER BY id")]

    ITEM_SELECT = """
        SELECT i.id, i.kind, i.title, i.description, i.report_date, i.status,
               i.image_key AS image, c.name AS category, l.name AS location
        FROM items AS i
        JOIN categories AS c ON c.id = i.category_id
        JOIN locations AS l ON l.id = i.location_id
    """

    def list_items(self, filters=None):
        filters = filters or {}
        conditions, values = [], []
        query = filters.get("q", "").strip()
        if query:
            conditions.append("instr(lower(i.title || ' ' || i.description || ' ' || l.name), lower(?)) > 0")
            values.append(query)
        for key, column in (("kind", "i.kind"), ("category", "c.name"), ("location", "l.name")):
            if filters.get(key):
                conditions.append(f"{column} = ?")
                values.append(filters[key])
        sql = self.ITEM_SELECT
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY i.report_date DESC, i.id DESC"
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(sql, values)]

    def get_item(self, item_id):
        with self.connection() as connection:
            row = connection.execute(self.ITEM_SELECT + " WHERE i.id = ?", (item_id,)).fetchone()
            return dict(row) if row else None

    def create_item(self, data):
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute("""
                    INSERT INTO items
                        (reporter_id, category_id, location_id, title, description, kind, report_date)
                    VALUES (
                        (SELECT id FROM users WHERE email = ?),
                        (SELECT id FROM categories WHERE name = ?),
                        (SELECT id FROM locations WHERE name = ?),
                        ?, ?, ?, ?
                    )
                """, (DEMO_REPORTER_EMAIL, data["category"], data["location"],
                      data["title"], data["description"], data["kind"], data["report_date"]))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return self.get_item(cursor.lastrowid)

    def submit_claim(self, item_id, data):
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                item = connection.execute(
                    "SELECT id FROM items WHERE id = ? AND kind = 'Found' AND status = 'Open'",
                    (item_id,),
                ).fetchone()
                if item is None:
                    connection.rollback()
                    return None
                connection.execute("""
                    INSERT INTO users(name, email) VALUES (?, ?)
                    ON CONFLICT(email) DO NOTHING
                """, (data["name"], data["contact"]))
                claimant_id = connection.execute(
                    "SELECT id FROM users WHERE email = ?", (data["contact"],)
                ).fetchone()[0]
                cursor = connection.execute("""
                    INSERT INTO claims(item_id, claimant_id, explanation)
                    VALUES (?, ?, ?)
                """, (item_id, claimant_id, data["explanation"]))
                connection.commit()
            except Exception:
                connection.rollback()
                raise
        return {"id": cursor.lastrowid}

    def list_claims(self):
        with self.connection() as connection:
            rows = connection.execute("""
                SELECT cl.id, cl.item_id, cl.explanation, cl.status, cl.created_at,
                       u.name, u.email AS contact, i.title AS item_title
                FROM claims AS cl
                JOIN users AS u ON u.id = cl.claimant_id
                JOIN items AS i ON i.id = cl.item_id
                ORDER BY cl.id DESC
            """).fetchall()
        return [dict(**{key: row[key] for key in row.keys() if key != "item_title"},
                     item={"title": row["item_title"]}) for row in rows]

    def review_claim(self, claim_id, action):
        if action not in ("approve", "reject"):
            return False
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                row = connection.execute("""
                    SELECT cl.status, i.kind, i.status AS item_status
                    FROM claims AS cl JOIN items AS i ON i.id = cl.item_id
                    WHERE cl.id = ?
                """, (claim_id,)).fetchone()
                if row is None or row["status"] != "Pending" or (action == "approve" and
                    (row["kind"] != "Found" or row["item_status"] != "Open")):
                    connection.rollback()
                    return False
                connection.execute(
                    "UPDATE claims SET status = ? WHERE id = ?",
                    ("Approved" if action == "approve" else "Rejected", claim_id),
                )
                # The approval trigger returns the item and rejects competing pending claims.
                connection.commit()
                return True
            except sqlite3.IntegrityError:
                connection.rollback()
                return False
            except Exception:
                connection.rollback()
                raise
