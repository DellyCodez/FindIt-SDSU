"""Known fictional pairs and safe upgrade checks for possible matches."""

from contextlib import closing
from datetime import date, timedelta

from app import create_app
from app.init_db import initialize_database
from app.matching import possible_matches
from app.storage import SQLiteStore, connect


def report(store, kind, title, description, category="Drinkware", location="Library", days_ago=0):
    return store.create_item(dict(
        kind=kind, title=title, description=description,
        category=category, location=location,
        report_date=(date.today() - timedelta(days=days_ago)).isoformat(),
    ))


def test_known_pair_reasons_and_false_leads(tmp_path):
    path = initialize_database(tmp_path / "matching.sqlite3")
    store = SQLiteStore(path)
    lost = store.get_item(1)  # fictional red water bottle in Library
    found = report(store, "Found", "Red water bottle",
                   "A matte red bottle with a dark loop lid.")
    report(store, "Found", "Blue water bottle",
           "A blue bottle with a silver lid.")
    report(store, "Found", "Red water bottle",
           "A matte red bottle found long before the loss.", days_ago=80)
    report(store, "Found", "Red water bottle",
           "A matte red bottle in another category.", category="Other")
    report(store, "Lost", "Red water bottle",
           "Another lost red bottle near the library.")

    matches = possible_matches(store, lost)
    assert [match["item"]["id"] for match in matches] == [found["id"]]
    assert matches[0]["score"] >= 60
    assert "Same category" in matches[0]["reasons"]
    assert "Same location" in matches[0]["reasons"]
    assert "red" in matches[0]["reasons"][-1]
    reverse = possible_matches(store, found)
    assert lost["id"] in [match["item"]["id"] for match in reverse]
    assert all(match["item"]["kind"] == "Lost" for match in reverse)
    assert [match["item"]["id"] for match in possible_matches(SQLiteStore(path), lost)] == [found["id"]]

    page = create_app(store).test_client().get(f"/items/{lost['id']}")
    assert b"Possible matches" in page.data
    assert b"Red water bottle" in page.data
    assert b"Match score" in page.data
    assert b"proof of ownership" in page.data


def test_public_evidence_ranking_returned_items_and_private_claims(tmp_path):
    store = SQLiteStore(initialize_database(tmp_path / "ranking.sqlite3"))
    lost = report(store, "Lost", "Purple jacket with moon patch",
                  "Purple jacket with an embroidered moon patch and orange zipper.",
                  category="Clothing", days_ago=20)
    best = report(store, "Found", "Purple jacket with moon patch",
                  "Purple jacket with a moon patch and orange zipper.",
                  category="Clothing", days_ago=19)
    away = report(store, "Found", "Purple jacket with moon patch",
                  "Purple jacket with a moon patch and orange zipper.",
                  category="Clothing", location="Campus Green", days_ago=19)
    later = report(store, "Found", "Purple jacket with moon patch",
                   "Purple jacket with a moon patch and orange zipper.",
                   category="Clothing", days_ago=0)
    color_only = report(store, "Found", "Purple scarf",
                        "Purple wool scarf with tassels.",
                        category="Clothing", days_ago=19)
    report(store, "Lost", "Purple jacket with moon patch",
           "Purple jacket with a moon patch and orange zipper.",
           category="Clothing", days_ago=19)

    matches = possible_matches(store, lost, limit=10)
    by_id = {match["item"]["id"]: match for match in matches}
    assert best["id"] == matches[0]["item"]["id"]
    assert set(by_id) == {best["id"], away["id"], later["id"]}
    assert by_id[best["id"]]["score"] > by_id[away["id"]]["score"]
    assert by_id[best["id"]]["score"] > by_id[later["id"]]["score"]
    assert "Same location" in by_id[best["id"]]["reasons"]
    assert "Same location" not in by_id[away["id"]]["reasons"]
    assert "Dates close together" not in by_id[later["id"]]["reasons"]
    assert color_only["id"] not in by_id
    assert all(match["item"]["kind"] == "Found" for match in matches)
    assert all(match["item"]["kind"] == "Lost" for match in possible_matches(store, best))

    private_detail = "A stitched name hidden under the inside collar."
    claim = store.submit_claim(best["id"], dict(
        name="Fictional Claimant", contact="claimant@example.test",
        explanation=private_detail))
    client = create_app(store).test_client()
    assert private_detail.encode() not in client.get(f"/items/{lost['id']}").data
    assert private_detail.encode() not in client.get(f"/items/{best['id']}").data
    assert private_detail.encode() in client.get("/review/claims").data
    assert store.review_claim(claim["id"], "approve")
    assert store.get_item(best["id"])["status"] == "Returned"
    assert best["id"] not in [m["item"]["id"] for m in possible_matches(store, lost, limit=10)]
    assert possible_matches(store, store.get_item(best["id"])) == []


def test_relevance_sort_and_active_filters(tmp_path):
    store = SQLiteStore(initialize_database(tmp_path / "sort.sqlite3"))
    older = report(store, "Lost", "Canvas camera pouch",
                   "A canvas pouch used for my camera.", days_ago=10)
    newer = report(store, "Lost", "Black tote bag",
                   "A black tote bag carrying a camera pouch.", days_ago=0)
    assert [item["id"] for item in store.list_items({"q": "camera", "sort": "oldest"})] == [older["id"], newer["id"]]
    assert [item["id"] for item in store.list_items({"q": "camera", "sort": "newest"})] == [newer["id"], older["id"]]
    assert [item["id"] for item in store.list_items({"q": "camera", "sort": "relevance"})] == [older["id"], newer["id"]]
    page = create_app(store).test_client().get("/items?q=camera&kind=Lost&sort=relevance")
    assert b"Filtering by" in page.data
    assert b"Best match" in page.data
    assert page.data.index(b"Canvas camera pouch") < page.data.index(b"Black tote bag")


def test_existing_database_upgrades_without_losing_records(tmp_path):
    path = initialize_database(tmp_path / "upgrade.sqlite3")
    store = SQLiteStore(path)
    added = report(store, "Found", "Green notebook",
                   "A green notebook with a paper bookmark.", category="Other")
    store.submit_claim(added["id"], dict(name="Fictional Student",
                       contact="fictional@example.test",
                       explanation="There is a small drawing on page three."))
    with closing(connect(path)) as connection:
        tables = ("users", "categories", "locations", "items", "claims")
        before = {table: [tuple(row) for row in connection.execute(
            f"SELECT * FROM {table} ORDER BY id")] for table in tables}
        connection.execute("DROP INDEX idx_items_match_candidates")
        connection.execute("PRAGMA user_version = 1")
    initialize_database(path)
    upgraded = SQLiteStore(path)
    assert upgraded.get_item(added["id"])["title"] == "Green notebook"
    assert len(upgraded.list_claims()) == 1
    initialize_database(path)  # repeat setup must not duplicate fixtures or claims
    assert len(upgraded.list_items()) == 7
    with closing(connect(path)) as connection:
        assert {table: [tuple(row) for row in connection.execute(
            f"SELECT * FROM {table} ORDER BY id")] for table in tables} == before
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        indexes = {row[1] for row in connection.execute("PRAGMA index_list(items)")}
        assert "idx_items_match_candidates" in indexes
        plan = " ".join(row[3] for row in connection.execute("""
            EXPLAIN QUERY PLAN SELECT id FROM items
            WHERE kind = ? AND status = 'Open' AND category_id = ?
              AND report_date BETWEEN ? AND ?
        """, ("Lost", 3, "2026-01-01", "2026-12-31")))
        assert "idx_items_match_candidates" in plan
