"""Web flow and SQLite integration checks for the local demonstration app."""

from datetime import date
from contextlib import closing
import sqlite3

import pytest

from app import create_app
from app.init_db import initialize_database
from app.storage import SQLiteStore, connect


def client_and_store(tmp_path):
    path = initialize_database(tmp_path / "findit.sqlite3")
    store = SQLiteStore(path)
    app = create_app(store)
    app.config.update(TESTING=True)
    return app.test_client(), store, path


def token(client):
    client.get("/")
    with client.session_transaction() as session:
        return session["csrf_token"]


def test_pages_and_filters(tmp_path):
    client, _, _ = client_and_store(tmp_path)
    for path in ("/", "/items", "/items/new", "/items/1", "/items/2/claim", "/review/claims"):
        assert client.get(path).status_code == 200
    assert client.get("/items/999").status_code == 404
    assert client.get("/items/1/claim").status_code == 404
    page = client.get("/items?q=earbuds&kind=Found&category=Electronics&location=Student+Union")
    assert b"Black wireless earbuds" in page.data
    assert b"Red water bottle" not in page.data
    assert b"No items found" in client.get("/items?q=unfindable").data


def test_report_claim_review_journey_and_privacy(tmp_path):
    client, store, path = client_and_store(tmp_path)
    csrf = token(client)
    assert client.post("/items/new", data={"title": "Bad", "csrf_token": csrf}).status_code == 200
    assert len(store.list_items()) == 6
    report = dict(csrf_token=csrf, kind="Found", title="Striped umbrella",
                  description="Navy and cream stripes with a wooden handle.",
                  category="Other", item_type="Other", location="Library", report_date=date.today().isoformat(),
                  contact_email="private-reporter@example.test")
    response = client.post("/items/new", data=report, follow_redirects=True)
    assert response.status_code == 200
    assert b"Striped umbrella" in response.data
    assert len(store.list_items()) == 7
    assert b"Striped umbrella" in client.get("/items?q=umbrella&kind=Found").data
    item_id = store.list_items({"q": "umbrella"})[0]["id"]
    assert b"private-reporter@example.test" not in client.get(f"/items/{item_id}").data
    assert b"private-reporter@example.test" not in client.get("/items?q=umbrella").data
    claim = dict(csrf_token=csrf, name="Demo Student", contact="demo@example.test",
                 explanation="The handle has a tiny star etched near the base.")
    assert client.post(f"/items/{item_id}/claim", data=claim, follow_redirects=True).status_code == 200
    assert client.post(f"/items/{item_id}/claim", data=claim).status_code == 409
    other_claim = {**claim, "name": "Second Fictional Student", "contact": "second@example.test"}
    assert client.post(f"/items/{item_id}/claim", data=other_claim, follow_redirects=True).status_code == 200
    assert b"tiny star" not in client.get(f"/items/{item_id}").data
    assert b"tiny star" in client.get("/review/claims").data
    assert b"private-reporter@example.test" in client.get("/review/claims").data
    assert client.post("/review/claims/1", data={"csrf_token": csrf, "action": "approve"}, follow_redirects=True).status_code == 200
    assert store.get_item(item_id)["status"] == "Returned"
    assert [claim["status"] for claim in store.list_claims()] == ["Rejected", "Approved"]
    assert client.post("/review/claims/2", data={"csrf_token": csrf, "action": "approve"}).status_code == 302
    assert store.get_item(item_id)["status"] == "Returned"
    assert client.get(f"/items/{item_id}/claim").status_code == 404
    # A new app/store instance reads the same reports and review decisions.
    restarted = SQLiteStore(path)
    assert restarted.get_item(item_id)["status"] == "Returned"
    assert len(restarted.list_claims()) == 2
    new_app = create_app(restarted)
    assert b"Striped umbrella" in new_app.test_client().get("/items?q=umbrella").data


def test_bad_input_and_csrf_rejected(tmp_path):
    client, store, _ = client_and_store(tmp_path)
    csrf = token(client)
    assert client.post("/items/new", data={"csrf_token": "wrong"}).status_code == 400
    invalid_report = client.post("/items/new", data=dict(csrf_token=csrf, kind="Lost", title="Future item",
        description="A made up item description", category="Other", location="Library",
        report_date="2999-01-01"))
    assert invalid_report.status_code == 200
    assert b'aria-invalid="true"' in invalid_report.data
    assert b"Please check the highlighted fields" in invalid_report.data
    assert len(store.list_items()) == 6
    exposed_contact = client.post("/items/new", data=dict(csrf_token=csrf, kind="Lost",
        title="Fictional item", description="Call 619-555-0123 to find this item.",
        category="Other", item_type="Other", location="Library", report_date=date.today().isoformat()))
    assert b"Keep email addresses and phone numbers out of public details" in exposed_contact.data
    assert len(store.list_items()) == 6
    compact_date = client.post("/items/new", data=dict(csrf_token=csrf, kind="Lost",
        title="Invalid date format", description="This fictional report has a compact date.",
        category="Other", location="Library", report_date=date.today().strftime("%Y%m%d")))
    assert compact_date.status_code == 200
    assert b"Choose a valid date" in compact_date.data
    assert len(store.list_items()) == 6
    invalid_claim = client.post("/items/2/claim", data=dict(csrf_token=csrf, name="A",
        contact="not-an-email", explanation="too short"))
    assert invalid_claim.status_code == 200
    assert b'aria-invalid="true"' in invalid_claim.data
    assert store.list_claims() == []


def test_lost_report_and_rejected_claim_survive_restart(tmp_path):
    client, store, path = client_and_store(tmp_path)
    csrf = token(client)
    response = client.post("/items/new", data=dict(
        csrf_token=csrf, kind="Lost", title="Purple pencil pouch",
        description="Small canvas pouch with a silver zipper.",
        category="Other", item_type="Other", location="Library", report_date=date.today().isoformat(),
    ), follow_redirects=True)
    assert response.status_code == 200
    lost_id = store.list_items({"q": "pencil pouch"})[0]["id"]
    assert store.get_item(lost_id)["kind"] == "Lost"
    assert client.get(f"/items/{lost_id}/claim").status_code == 404
    assert b"Purple pencil pouch" in client.get("/items?q=pencil&kind=Lost&location=Library").data

    assert client.post("/items/2/claim", data=dict(
        csrf_token=csrf, name="Fictional Student", contact="student@example.test",
        explanation="There is a white scratch on the inside of the case.",
    )).status_code == 302
    claim_id = store.list_claims()[0]["id"]
    assert client.post(f"/review/claims/{claim_id}", data={
        "csrf_token": csrf, "action": "reject",
    }).status_code == 302
    restarted = SQLiteStore(path)
    assert restarted.get_item(lost_id)["title"] == "Purple pencil pouch"
    assert restarted.get_item(2)["status"] == "Open"
    assert restarted.list_claims()[0]["status"] == "Rejected"


def test_database_constraints_and_repeatable_setup(tmp_path):
    client, store, path = client_and_store(tmp_path)
    initialize_database(path)
    assert len(store.list_items()) == 6  # setup preserves existing reports
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, report_date)
                VALUES (99999, 1, 1, 'Invalid item', 'This report has no reporter.',
                        'Lost', '2026-10-17')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, report_date)
                VALUES (1, 1, 1, 'Invalid item', 'This report has a bad status.',
                        'Borrowed', '2026-10-17')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO claims(item_id, claimant_id, explanation)
                VALUES (1, 1, 'A lost report cannot be claimed.')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO claims(item_id, claimant_id, explanation)
                VALUES (99999, 1, 'This report does not exist at all.')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, status, report_date)
                VALUES (1, 1, 1, 'Invalid item', 'This report starts as returned.',
                        'Found', 'Returned', '2026-10-17')
            """)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO items(reporter_id, category_id, location_id, title,
                                  description, kind, report_date)
                VALUES (1, 1, 1, 'Invalid item', 'This report has an invalid date.',
                        'Found', '2026-02-30')
            """)
    csrf = token(client)
    claim = dict(csrf_token=csrf, name="Demo Student", contact="demo@example.test",
                 explanation="A small silver mark is inside the case.")
    client.post("/items/2/claim", data=claim)
    client.post("/items/2/claim", data={**claim, "name": "Second Student", "contact": "second@example.test"})
    with closing(connect(path)) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE items SET kind = 'Lost' WHERE id = 2")
        connection.execute("UPDATE claims SET status = 'Approved' WHERE id = 1")
        assert connection.execute("SELECT status FROM items WHERE id = 2").fetchone()[0] == "Returned"
        assert connection.execute("SELECT status FROM claims WHERE id = 2").fetchone()[0] == "Rejected"
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE claims SET status = 'Approved' WHERE id = 2")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE claims SET item_id = 4 WHERE id = 1")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("DELETE FROM claims WHERE id = 1")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE items SET status = 'Open' WHERE id = 2")
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO claims(item_id, claimant_id, explanation)
                VALUES (2, 1, 'A returned item cannot be claimed.')
            """)
