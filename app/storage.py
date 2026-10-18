"""Small SQLite data layer matching the existing Flask page interface."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3
import time
from uuid import uuid4


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
    def __init__(self, path=None, upload_dir=None):
        self.path = Path(path or database_path()).resolve()
        self.upload_dir = Path(upload_dir or os.environ.get("FINDIT_UPLOAD_DIR") or
                               self.path.parent / "uploads").expanduser().resolve()
        if not self.path.is_file():
            raise RuntimeError(f"Database missing at {self.path}. Run: python -m app.init_db")
        with self.connection() as connection:
            if connection.execute("PRAGMA user_version").fetchone()[0] != 8:
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

    def reserve_submission(self, action, actor_key, limit, window_seconds):
        """Atomically count attempts across workers without storing a raw address."""
        now = int(time.time())
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                connection.execute("DELETE FROM submission_attempts WHERE created_at < ?", (now - 86400,))
                count = connection.execute("""SELECT COUNT(*) FROM submission_attempts
                    WHERE action = ? AND actor_key = ? AND created_at > ?""",
                    (action, actor_key, now - window_seconds)).fetchone()[0]
                if count >= limit:
                    connection.rollback()
                    return False
                connection.execute("""INSERT INTO submission_attempts(action, actor_key, created_at)
                    VALUES (?, ?, ?)""", (action, actor_key, now))
                connection.commit()
                return True
            except Exception:
                connection.rollback()
                raise

    def list_locations(self):
        with self.connection() as connection:
            return [row[0] for row in connection.execute("SELECT name FROM locations ORDER BY id")]

    ITEM_SELECT = """
        SELECT i.id, i.kind, i.title, i.description, i.report_date, i.status,
               i.category_id, i.location_id, i.item_type, i.brand, i.model, i.color,
               i.distinguishing_features,
               i.image_key AS image, c.name AS category, l.name AS location,
               cover.id AS photo_id
        FROM items AS i
        JOIN categories AS c ON c.id = i.category_id
        JOIN locations AS l ON l.id = i.location_id
        LEFT JOIN item_photos AS cover ON cover.item_id = i.id AND cover.position = 1
    """

    def list_items(self, filters=None):
        filters = filters or {}
        conditions, values = ["i.visibility = 'Visible'"], []
        query = filters.get("q", "").strip()
        if query:
            conditions.append("instr(lower(i.title || ' ' || i.description || ' ' || coalesce(i.distinguishing_features, '') || ' ' || l.name || ' ' || coalesce(i.brand, '') || ' ' || coalesce(i.model, '')), lower(?)) > 0")
            values.append(query)
        for key, column in (("kind", "i.kind"), ("category", "c.name"), ("location", "l.name")):
            if filters.get(key):
                conditions.append(f"{column} = ?")
                values.append(filters[key])
        if filters.get("status") in ("Open", "Returned"):
            conditions.append("i.status = ?")
            values.append(filters["status"])
        sql = self.ITEM_SELECT
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sort = filters.get("sort", "newest")
        if sort == "oldest":
            sql += " ORDER BY i.report_date ASC, i.id ASC"
        elif sort == "relevance" and query:
            sql += " ORDER BY CASE WHEN instr(lower(i.title), lower(?)) > 0 THEN 0 ELSE 1 END, i.report_date DESC, i.id DESC"
            values.append(query)
        else:
            sql += " ORDER BY i.report_date DESC, i.id DESC"
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(sql, values)]

    def match_candidates(self, item, first_date, last_date):
        """Fetch plausible opposite-type reports using the composite matching index."""
        kind = "Found" if item["kind"] == "Lost" else "Lost"
        sql = self.ITEM_SELECT + """
            WHERE i.kind = ? AND i.status = 'Open' AND i.visibility = 'Visible' AND i.category_id = ?
              AND i.report_date BETWEEN ? AND ? AND i.id != ?
        """
        values = [kind, item["category_id"], first_date, last_date, item["id"]]
        if item.get("item_type") and item["item_type"] != "Other":
            sql += " AND (i.item_type = ? OR i.item_type IS NULL OR i.item_type = 'Other')"
            values.append(item["item_type"])
        sql += " ORDER BY i.report_date DESC, i.id DESC LIMIT 300"
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(sql, values)]

    def get_item(self, item_id):
        with self.connection() as connection:
            row = connection.execute(self.ITEM_SELECT + " WHERE i.id = ? AND i.visibility = 'Visible'", (item_id,)).fetchone()
            return dict(row) if row else None

    def list_photos(self, item_id):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("""
                SELECT id, item_id, position, width, height FROM item_photos
                WHERE item_id = ? ORDER BY position
            """, (item_id,))]

    def get_photo(self, photo_id):
        with self.connection() as connection:
            row = connection.execute("""
                SELECT p.file_name, p.mime_type FROM item_photos AS p
                JOIN items AS i ON i.id = p.item_id
                WHERE p.id = ? AND i.visibility = 'Visible'
            """, (photo_id,)).fetchone()
            return dict(row) if row else None

    def create_item(self, data, photos=None):
        photos = photos or []
        if len(photos) > 3:
            raise ValueError("An item can have at most three photos")
        written = []
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute("""
                    INSERT INTO items
                        (reporter_id, category_id, location_id, title, description, kind,
                         report_date, item_type, brand, model, color, contact_email,
                         distinguishing_features)
                    VALUES (
                        (SELECT id FROM users WHERE email = ?),
                        (SELECT id FROM categories WHERE name = ?),
                        (SELECT id FROM locations WHERE name = ?),
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (DEMO_REPORTER_EMAIL, data["category"], data["location"],
                      data["title"], data["description"], data["kind"], data["report_date"],
                      data.get("item_type") or None, data.get("brand") or None,
                      data.get("model") or None, data.get("color") or None,
                      data.get("contact_email") or None,
                      data.get("distinguishing_features") or None))
                if photos:
                    self.upload_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
                    for position, photo in enumerate(photos, 1):
                        file_name = uuid4().hex + ".webp"
                        path = self.upload_dir / file_name
                        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                        with os.fdopen(descriptor, "wb") as output:
                            written.append(path)
                            output.write(photo["data"])
                        connection.execute("""
                            INSERT INTO item_photos
                                (item_id, file_name, position, mime_type, width, height, byte_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (cursor.lastrowid, file_name, position, photo["mime_type"],
                              photo["width"], photo["height"], photo["byte_count"]))
                connection.commit()
            except Exception:
                connection.rollback()
                for path in written:
                    path.unlink(missing_ok=True)
                raise
        return self.get_item(cursor.lastrowid)

    def submit_claim(self, item_id, data):
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                item = connection.execute(
                    "SELECT id FROM items WHERE id = ? AND kind = 'Found' AND status = 'Open' AND visibility = 'Visible'",
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
                if connection.execute(
                    "SELECT 1 FROM claims WHERE item_id = ? AND claimant_id = ?",
                    (item_id, claimant_id),
                ).fetchone():
                    connection.rollback()
                    return {"error": "duplicate"}
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
                       u.name, u.email AS contact, i.title AS item_title,
                       i.status AS item_status, i.visibility AS item_visibility,
                       i.contact_email AS reporter_contact,
                       CASE WHEN i.visibility = 'Visible' THEN cover.id END AS photo_id
                FROM claims AS cl
                JOIN users AS u ON u.id = cl.claimant_id
                JOIN items AS i ON i.id = cl.item_id
                LEFT JOIN item_photos AS cover ON cover.item_id = i.id AND cover.position = 1
                ORDER BY cl.id DESC
            """).fetchall()
        return [dict(**{key: row[key] for key in row.keys() if key != "item_title"},
                     item={"title": row["item_title"]}) for row in rows]

    def list_moderation_items(self):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("""
                SELECT i.id, i.title, i.kind, i.status, i.visibility, i.report_date,
                       i.description, c.name AS category, l.name AS location
                FROM items AS i
                JOIN categories AS c ON c.id = i.category_id
                JOIN locations AS l ON l.id = i.location_id
                ORDER BY i.id DESC
            """)]

    def set_item_visibility(self, item_id, visibility):
        if visibility not in ("Visible", "Hidden"):
            return False
        with self.connection() as connection:
            cursor = connection.execute(
                "UPDATE items SET visibility = ? WHERE id = ? AND visibility != ?",
                (visibility, item_id, visibility),
            )
            return cursor.rowcount == 1

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
