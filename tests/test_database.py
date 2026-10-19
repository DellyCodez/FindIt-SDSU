"""Dedicated QA and database verification tests for FindIt SDSU.

These tests independently verify SQLite constraints, triggers, foreign keys,
concurrency safety, and execution performance against database/schema.sql.
"""

from contextlib import closing
from datetime import date
import sqlite3

import pytest

from app.init_db import initialize_database
from app.storage import SQLiteStore, connect
from database.evaluate import run as run_database_evaluation


# ==============================================================================
# SECTION: BENCHMARKS & QUERY PLANS
# ==============================================================================

# Benchmark: verifies synthetic generation (4,800 rows), foreign key pragma, and candidate index performance.
def test_database_evaluation_benchmark_and_query_plans():
    run_database_evaluation()


# ==============================================================================
# SECTION: DATA INTEGRITY & BOUNDARY CHECKS
# ==============================================================================

# Boundary: verifies strict CHECK constraints on user email regex and valid ISO calendar dates.
def test_schema_constraints_email_and_dates(tmp_path):
    path = initialize_database(tmp_path / "constraints.sqlite3")
    with closing(connect(path)) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO users(name, email) VALUES ('Bad User', 'invalid-email-address')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO users(name, email) VALUES ('Space User', 'user with spaces@example.com')")

        conn.execute("INSERT INTO users(name, email) VALUES ('Valid User', 'valid.user@sdsu.edu')")

        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, report_date)
                VALUES (1, 1, 1, 'Impossible Date Item', 'Testing impossible calendar date.',
                        'Lost', '2026-02-30')
            """)

        conn.execute("""
            INSERT INTO items(reporter_id, category_id, location_id, title,
                              description, kind, report_date)
            VALUES (1, 1, 1, 'Valid Date Item', 'Testing valid calendar date.',
                    'Lost', '2026-10-18')
        """)


# Boundary & Corruption: verifies string length checks, trim constraints, and disallows empty or whitespace-only names/titles.
def test_schema_string_boundaries_and_empty_field_rejection(tmp_path):
    path = initialize_database(tmp_path / "string_bounds.sqlite3")
    with closing(connect(path)) as conn:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO users(name, email) VALUES ('   ', 'empty@sdsu.edu')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO categories(name) VALUES ('   ')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO locations(name) VALUES ('')")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title, description, kind, report_date)
                VALUES (1, 1, 1, 'abc', 'Short description here.', 'Lost', '2026-10-18')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title, description, kind, report_date)
                VALUES (1, 1, 1, 'Valid Title', 'Short', 'Lost', '2026-10-18')
            """)


# ==============================================================================
# SECTION: STATE TRANSITIONS & LIFECYCLE TRIGGERS
# ==============================================================================

# State lifecycle: verifies triggers enforcing report starts Open, immutable claim identity, and no reopening approved items.
def test_schema_triggers_lifecycle_and_immutability(tmp_path):
    path = initialize_database(tmp_path / "triggers.sqlite3")
    with closing(connect(path)) as conn:
        with pytest.raises(sqlite3.IntegrityError, match="a new report must start open"):
            conn.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, status, report_date)
                VALUES (1, 1, 1, 'Bad Start Item', 'Should not start as returned.',
                        'Found', 'Returned', '2026-10-18')
            """)

        cursor = conn.execute("""
            INSERT INTO items(reporter_id, category_id, location_id, title,
                              description, kind, status, report_date)
            VALUES (1, 1, 1, 'Found Sunglasses', 'Black sunglasses found on bench.',
                    'Found', 'Open', '2026-10-18')
        """)
        item_id = cursor.lastrowid

        conn.execute("INSERT INTO users(name, email) VALUES ('Claimant A', 'claimant.a@example.com')")
        conn.execute("INSERT INTO users(name, email) VALUES ('Claimant B', 'claimant.b@example.com')")
        user_a = conn.execute("SELECT id FROM users WHERE email='claimant.a@example.com'").fetchone()[0]
        user_b = conn.execute("SELECT id FROM users WHERE email='claimant.b@example.com'").fetchone()[0]

        cursor_a = conn.execute("INSERT INTO claims(item_id, claimant_id, explanation) VALUES (?, ?, ?)",
                                (item_id, user_a, 'Distinct scratch on the left lens frame.'))
        claim_a_id = cursor_a.lastrowid

        cursor_b = conn.execute("INSERT INTO claims(item_id, claimant_id, explanation) VALUES (?, ?, ?)",
                                (item_id, user_b, 'Has a tiny case with a red sticker.'))
        claim_b_id = cursor_b.lastrowid

        with pytest.raises(sqlite3.IntegrityError, match="an item with claims cannot change kind"):
            conn.execute("UPDATE items SET kind = 'Lost' WHERE id = ?", (item_id,))

        with pytest.raises(sqlite3.IntegrityError, match="a claim cannot change its item or claimant"):
            conn.execute("UPDATE claims SET item_id = 999 WHERE id = ?", (claim_a_id,))

        conn.execute("UPDATE claims SET status = 'Approved' WHERE id = ?", (claim_a_id,))
        assert conn.execute("SELECT status FROM items WHERE id = ?", (item_id,)).fetchone()[0] == 'Returned'
        assert conn.execute("SELECT status FROM claims WHERE id = ?", (claim_b_id,)).fetchone()[0] == 'Rejected'

        with pytest.raises(sqlite3.IntegrityError, match="an approved claim cannot be deleted"):
            conn.execute("DELETE FROM claims WHERE id = ?", (claim_a_id,))

        with pytest.raises(sqlite3.IntegrityError, match="an approved item cannot be reopened"):
            conn.execute("UPDATE items SET status = 'Open' WHERE id = ?", (item_id,))


# Concurrency & Invariants: verifies partial unique index one_approved_claim_per_item prevents multiple approved claims.
def test_partial_unique_index_single_approved_claim(tmp_path):
    path = initialize_database(tmp_path / "single_approval.sqlite3")
    with closing(connect(path)) as conn:
        conn.execute("""
            INSERT INTO items(reporter_id, category_id, location_id, title, description, kind, status, report_date)
            VALUES (1, 1, 1, 'Found Keys', 'A set of brass keys with SDSU lanyard.', 'Found', 'Open', '2026-10-18')
        """)
        item_id = conn.execute("SELECT id FROM items WHERE title='Found Keys'").fetchone()[0]
        conn.execute("INSERT INTO users(name, email) VALUES ('User 1', 'u1@sdsu.edu')")
        conn.execute("INSERT INTO users(name, email) VALUES ('User 2', 'u2@sdsu.edu')")
        u1_id = conn.execute("SELECT id FROM users WHERE email='u1@sdsu.edu'").fetchone()[0]
        u2_id = conn.execute("SELECT id FROM users WHERE email='u2@sdsu.edu'").fetchone()[0]

        c1 = conn.execute("INSERT INTO claims(item_id, claimant_id, explanation) VALUES (?, ?, ?)",
                          (item_id, u1_id, 'Has a red SDSU tag attached.')).lastrowid
        c2 = conn.execute("INSERT INTO claims(item_id, claimant_id, explanation) VALUES (?, ?, ?)",
                          (item_id, u2_id, 'Has an SDSU logo on the ring.')).lastrowid

        conn.execute("UPDATE claims SET status='Approved' WHERE id = ?", (c1,))
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("UPDATE claims SET status='Approved' WHERE id = ?", (c2,))


# ==============================================================================
# SECTION: FOREIGN KEY CASCADE & REFERENTIAL INTEGRITY
# ==============================================================================

# Referential integrity: verifies PRAGMA foreign_keys = ON blocks orphan child records and cascades photo deletion.
def test_foreign_key_delete_restrict_and_cascade(tmp_path):
    path = initialize_database(tmp_path / "fk_cascade.sqlite3")
    with closing(connect(path)) as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title, description, kind, report_date)
                VALUES (9999, 1, 1, 'Orphan Item', 'This reporter does not exist.', 'Lost', '2026-10-18')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM categories WHERE id = 1")
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("DELETE FROM locations WHERE id = 1")

        item_id = conn.execute("SELECT id FROM items LIMIT 1").fetchone()[0]
        fake_photo = "f" * 32 + ".webp"
        conn.execute("""
            INSERT INTO item_photos(item_id, file_name, position, mime_type, width, height, byte_count)
            VALUES (?, ?, 1, 'image/webp', 80, 80, 500)
        """, (item_id, fake_photo))
        assert conn.execute("SELECT COUNT(*) FROM item_photos WHERE item_id = ?", (item_id,)).fetchone()[0] == 1
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        assert conn.execute("SELECT COUNT(*) FROM item_photos WHERE item_id = ?", (item_id,)).fetchone()[0] == 0
