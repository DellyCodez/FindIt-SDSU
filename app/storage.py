"""Small SQLite data layer matching the existing Flask page interface."""

from contextlib import contextmanager
import os
from pathlib import Path
import re
import secrets
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
        self.upload_dir = Path(os.environ.get("FINDIT_UPLOAD_DIR", self.path.parent / "uploads")).resolve()
        if not self.path.is_file():
            raise RuntimeError(f"Database missing at {self.path}. Run: python -m app.init_db")
        with self.connection() as connection:
            if connection.execute("PRAGMA user_version").fetchone()[0] != 4:
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
               i.item_type, i.brand, i.model, i.primary_color, i.distinguishing_features,
               i.category_id, i.location_id,
               i.image_key AS image, c.name AS category, l.name AS location,
               (SELECT p.id FROM item_photos AS p WHERE p.item_id = i.id
                ORDER BY p.position LIMIT 1) AS photo_id
        FROM items AS i
        JOIN categories AS c ON c.id = i.category_id
        JOIN locations AS l ON l.id = i.location_id
    """

    def list_items(self, filters=None):
        filters = filters or {}
        conditions, values = [], []
        query = filters.get("q", "").strip()
        if query:
            conditions.append("instr(lower(i.title || ' ' || i.description || ' ' || coalesce(i.item_type,'') || ' ' || coalesce(i.brand,'') || ' ' || coalesce(i.model,'') || ' ' || l.name), lower(?)) > 0")
            values.append(query)
        for key, column in (("kind", "i.kind"), ("category", "c.name"), ("location", "l.name")):
            if filters.get(key):
                conditions.append(f"{column} = ?")
                values.append(filters[key])
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
            WHERE i.kind = ? AND i.status = 'Open' AND i.category_id = ?
              AND (i.item_type = ? OR i.item_type IS NULL OR i.item_type = 'Other' OR ? IS NULL)
              AND i.report_date BETWEEN ? AND ? AND i.id != ?
            ORDER BY i.report_date DESC, i.id DESC LIMIT 300
        """
        item_type = item.get("item_type") if item.get("item_type") != "Other" else None
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(
                sql, (kind, item["category_id"], item_type, item_type,
                      first_date, last_date, item["id"])
            )]

    def get_item(self, item_id):
        with self.connection() as connection:
            row = connection.execute(self.ITEM_SELECT + " WHERE i.id = ?", (item_id,)).fetchone()
            return dict(row) if row else None

    def get_photos(self, item_id):
        with self.connection() as connection:
            return [dict(row) for row in connection.execute("""
                SELECT id, item_id, position, width, height, byte_size
                FROM item_photos WHERE item_id = ? ORDER BY position
            """, (item_id,))]

    def photo_path(self, item_id, photo_id):
        with self.connection() as connection:
            row = connection.execute(
                "SELECT filename FROM item_photos WHERE id = ? AND item_id = ?",
                (photo_id, item_id),
            ).fetchone()
        if row is None or not re.fullmatch(r"[0-9a-f]{32}\.webp", row["filename"]):
            return None
        path = self.upload_dir / row["filename"]
        return None if path.is_symlink() else path

    def create_item(self, data, photos=()):
        if len(photos) > 3:
            raise ValueError("A report can have at most three photos")
        written = []
        with self.connection() as connection:
            try:
                connection.execute("BEGIN IMMEDIATE")
                cursor = connection.execute("""
                    INSERT INTO items
                        (reporter_id, category_id, location_id, title, description, kind, report_date,
                         item_type, brand, model, primary_color, distinguishing_features)
                    VALUES (
                        (SELECT id FROM users WHERE email = ?),
                        (SELECT id FROM categories WHERE name = ?),
                        (SELECT id FROM locations WHERE name = ?),
                        ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (DEMO_REPORTER_EMAIL, data["category"], data["location"],
                      data["title"], data["description"], data["kind"], data["report_date"],
                      data.get("item_type"), data.get("brand") or None, data.get("model") or None,
                      data.get("primary_color") or None, data.get("distinguishing_features") or None))
                if photos:
                    self.upload_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
                for position, photo in enumerate(photos, start=1):
                    filename = secrets.token_hex(16) + ".webp"
                    path = self.upload_dir / filename
                    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                    written.append(path)
                    with os.fdopen(fd, "wb") as output:
                        output.write(photo["content"])
                    connection.execute("""
                        INSERT INTO item_photos(item_id, position, filename, width, height, byte_size)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (cursor.lastrowid, position, filename, photo["width"],
                          photo["height"], len(photo["content"])))
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
                       i.kind AS item_kind, i.status AS item_status,
                       i.report_date, i.image_key AS item_image,
                       i.item_type, i.brand, i.model, i.primary_color,
                       c.name AS category, l.name AS location,
                       (SELECT p.id FROM item_photos p WHERE p.item_id = i.id
                        ORDER BY p.position LIMIT 1) AS photo_id
                FROM claims AS cl
                JOIN users AS u ON u.id = cl.claimant_id
                JOIN items AS i ON i.id = cl.item_id
                JOIN categories AS c ON c.id = i.category_id
                JOIN locations AS l ON l.id = i.location_id
                ORDER BY cl.id DESC
            """).fetchall()
        claim_fields = ("id", "item_id", "explanation", "status", "created_at", "name", "contact")
        return [dict(**{key: row[key] for key in claim_fields}, item={
            "id": row["item_id"], "title": row["item_title"], "kind": row["item_kind"],
            "status": row["item_status"], "report_date": row["report_date"],
            "image": row["item_image"], "item_type": row["item_type"],
            "brand": row["brand"], "model": row["model"],
            "primary_color": row["primary_color"], "category": row["category"],
            "location": row["location"], "photo_id": row["photo_id"],
        }) for row in rows]

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
