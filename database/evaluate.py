"""Reproducible SQLite evaluation in an isolated, disposable database.

Run from the repository root: python -m database.evaluate
No normal demo records are read or modified.
"""

from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
import random
import sqlite3
from statistics import median
from tempfile import TemporaryDirectory
from time import perf_counter_ns

from app.init_db import initialize_database
from app.matching import possible_matches
from app.storage import SQLiteStore, connect


ANCHOR = date(2026, 8, 1)
RECORDS = 4800
PAIRS = (
    ("Drinkware", "Library", "Red thermos with yellow star", "A red thermos with a yellow star sticker on the base.", "Water Bottle", "Red"),
    ("Bags", "Student Union", "Green backpack with moon patch", "A green canvas backpack with an embroidered moon patch.", "Backpack", "Green"),
    ("Electronics", "Engineering Building", "Silver laptop with blue strap", "A silver laptop in a sleeve with a blue striped strap.", "Laptop", "Silver"),
    ("Keys", "West Commons", "Brass keys on orange cord", "Two brass keys attached to an orange woven cord.", "Keys", "Gold"),
    ("Clothing", "Campus Green", "Purple jacket with white zipper", "A purple jacket with a distinctive white front zipper.", "Clothing", "Purple"),
    ("Other", "Arts and Letters", "Yellow notebook with sun drawing", "A yellow notebook with a small sun drawing on the cover.", "Notebook", "Yellow"),
)

CANDIDATE_SQL = """
    SELECT i.id FROM items AS i {index_hint}
    WHERE i.kind = ? AND i.status = 'Open' AND i.category_id = ?
      AND i.report_date BETWEEN ? AND ?
    ORDER BY i.report_date DESC LIMIT 300
"""

JOIN_SQL = """
    SELECT i.id, i.title, c.name AS category, l.name AS location
    FROM items i JOIN categories c ON c.id = i.category_id
                 JOIN locations l ON l.id = i.location_id
    WHERE i.kind = 'Found' AND c.name = 'Drinkware' AND i.report_date >= '2026-08-01'
    ORDER BY i.report_date DESC LIMIT 5
"""

AGGREGATE_SQL = """
    SELECT l.name AS location, COUNT(*) AS reports,
           SUM(CASE WHEN i.kind = 'Found' THEN 1 ELSE 0 END) AS found_reports
    FROM items i JOIN locations l ON l.id = i.location_id
    GROUP BY l.id ORDER BY reports DESC LIMIT 5
"""


def populate(connection):
    rng = random.Random(514)
    categories = {row[1]: row[0] for row in connection.execute("SELECT id,name FROM categories")}
    locations = {row[1]: row[0] for row in connection.execute("SELECT id,name FROM locations")}
    category_names = sorted(categories)
    location_names = sorted(locations)
    rows = []
    for number in range(RECORDS):
        kind = "Lost" if rng.randrange(2) == 0 else "Found"
        category = category_names[number % len(category_names)]
        location = location_names[rng.randrange(len(location_names))]
        day = ANCHOR + timedelta(days=rng.randrange(55))
        rows.append((1, categories[category], locations[location],
                     f"Fictional sample object {number:04d}",
                     f"Synthetic {category.lower()} report number {number:04d} for query evaluation.",
                     kind, day.isoformat()))
    connection.executemany("""
        INSERT INTO items(reporter_id,category_id,location_id,title,description,kind,report_date)
        VALUES (?,?,?,?,?,?,?)
    """, rows)
    known = []
    for category, location, title, description, item_type, color in PAIRS:
        ids = []
        for kind, day in (("Lost", "2026-09-26"), ("Found", "2026-09-27")):
            cursor = connection.execute("""
                INSERT INTO items(reporter_id,category_id,location_id,title,description,kind,report_date,item_type,color)
                VALUES (1,?,?,?,?,?,?,?,?)
            """, (categories[category], locations[location], title, description, kind, day, item_type, color))
            ids.append(cursor.lastrowid)
        known.append(ids)
    return known


def measure(connection, sql, params, repetitions=200):
    for _ in range(12):
        connection.execute(sql, params).fetchall()
    timings = []
    for _ in range(repetitions):
        start = perf_counter_ns()
        connection.execute(sql, params).fetchall()
        timings.append((perf_counter_ns() - start) / 1_000_000)
    return median(timings)


def run():
    with TemporaryDirectory(prefix="findit-evaluation-") as directory:
        path = initialize_database(Path(directory) / "evaluation.sqlite3")
        with closing(connect(path)) as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("DELETE FROM items")  # only the disposable evaluation database
            known = populate(connection)
            connection.commit()
            connection.execute("ANALYZE")
            count = connection.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            assert count == RECORDS + 2 * len(PAIRS)
            print(f"Fictional evaluation reports: {count} in a temporary SQLite database")
            print("Foreign key check:", len(connection.execute("PRAGMA foreign_key_check").fetchall()), "violations")
            print("JOIN sample:", [tuple(row) for row in connection.execute(JOIN_SQL).fetchall()[:2]])
            print("Aggregate sample:", [tuple(row) for row in connection.execute(AGGREGATE_SQL).fetchall()[:2]])
            params = ("Found", 3, "2026-09-01", "2026-09-30")
            indexed = CANDIDATE_SQL.format(index_hint="INDEXED BY idx_items_match_candidates")
            scan = CANDIDATE_SQL.format(index_hint="NOT INDEXED")
            print("Indexed plan:", [row[3] for row in connection.execute("EXPLAIN QUERY PLAN " + indexed, params)])
            print("Scan plan:", [row[3] for row in connection.execute("EXPLAIN QUERY PLAN " + scan, params)])
            print(f"Median candidate query, 200 runs: indexed {measure(connection, indexed, params):.3f} ms; full scan {measure(connection, scan, params):.3f} ms")
            first_found = connection.execute("SELECT id FROM items WHERE kind='Found' ORDER BY id LIMIT 1").fetchone()[0]
            for suffix in ("one", "two"):
                connection.execute("INSERT INTO users(name,email) VALUES(?,?)",
                                   (f"Claimant {suffix}", f"{suffix}@example.test"))
                claimant_id = connection.execute("SELECT id FROM users WHERE email=?", (f"{suffix}@example.test",)).fetchone()[0]
                connection.execute("INSERT INTO claims(item_id,claimant_id,explanation) VALUES(?,?,?)",
                                   (first_found, claimant_id, "A distinctive fictional ownership detail."))
            claim_ids = [row[0] for row in connection.execute("SELECT id FROM claims WHERE item_id=? ORDER BY id", (first_found,))]
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("UPDATE claims SET status='Approved' WHERE id=?", (claim_ids[0],))
            status = connection.execute("SELECT status FROM items WHERE id=?", (first_found,)).fetchone()[0]
            decisions = [row[0] for row in connection.execute("SELECT status FROM claims WHERE item_id=? ORDER BY id", (first_found,))]
            assert status == "Returned" and decisions == ["Approved", "Rejected"]
            try:
                connection.execute("UPDATE claims SET status='Approved' WHERE id=?", (claim_ids[1],))
            except sqlite3.IntegrityError:
                print("Claim integrity: approval returned the item, rejected the competing claim, and blocked a second approval")
            else:
                raise AssertionError("second approval was accepted")
            connection.commit()
        store = SQLiteStore(path)
        correct = 0
        for known_lost, known_found in known:
            suggested = [match["item"]["id"] for match in possible_matches(store, store.get_item(known_lost), limit=3)]
            print(f"Known pair {known_lost}->{known_found}: suggestions {suggested}")
            correct += known_found in suggested
        print(f"Known-pair retrieval: {correct}/{len(known)} curated fictional pairs in top 3 suggestions")
        assert correct == len(known)
        phone = store.create_item(dict(kind="Lost", title="iPhone 14 Pro Max", description="Black phone with a chipped camera ring and crescent sticker.",
                                      category="Electronics", location="Library", report_date="2026-09-26", item_type="Smartphone", color="Black"))
        earbuds = store.create_item(dict(kind="Found", title="Black earbuds in case", description="Black case with a crescent sticker near the library.",
                                        category="Electronics", location="Library", report_date="2026-09-27", item_type="Earbuds", color="Black"))
        negative = earbuds["id"] not in [match["item"]["id"] for match in possible_matches(store, phone)]
        print("Curated incompatible-type false positive excluded:", negative)
        assert negative


if __name__ == "__main__":
    run()
