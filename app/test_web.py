"""Web flow checks for the temporary, in-memory demonstration app."""

from datetime import date

from app import create_app
from app.demo_store import DemoStore


def client_and_store():
    store = DemoStore()
    app = create_app(store)
    app.config.update(TESTING=True)
    return app.test_client(), store


def token(client):
    client.get("/")
    with client.session_transaction() as session:
        return session["csrf_token"]


def test_pages_and_filters():
    client, _ = client_and_store()
    for path in ("/", "/items", "/items/new", "/items/1", "/items/2/claim", "/review/claims"):
        assert client.get(path).status_code == 200
    assert client.get("/items/999").status_code == 404
    assert client.get("/items/1/claim").status_code == 404
    page = client.get("/items?q=earbuds&kind=Found&category=Electronics&location=Student+Union")
    assert b"Black wireless earbuds" in page.data
    assert b"Red water bottle" not in page.data
    assert b"No reports found" in client.get("/items?q=unfindable").data


def test_report_claim_review_journey_and_privacy():
    client, store = client_and_store()
    csrf = token(client)
    assert client.post("/items/new", data={"title": "Bad", "csrf_token": csrf}).status_code == 200
    assert len(store.list_items()) == 6
    report = dict(csrf_token=csrf, kind="Found", title="Striped umbrella",
                  description="Navy and cream stripes with a wooden handle.",
                  category="Other", location="Library", report_date=date.today().isoformat())
    response = client.post("/items/new", data=report, follow_redirects=True)
    assert response.status_code == 200
    assert b"Striped umbrella" in response.data
    assert len(store.list_items()) == 7
    assert b"Striped umbrella" in client.get("/items?q=umbrella&kind=Found").data
    item_id = store.list_items({"q": "umbrella"})[0]["id"]
    claim = dict(csrf_token=csrf, name="Demo Student", contact="demo@example.test",
                 explanation="The handle has a tiny star etched near the base.")
    assert client.post(f"/items/{item_id}/claim", data=claim, follow_redirects=True).status_code == 200
    assert client.post(f"/items/{item_id}/claim", data=claim, follow_redirects=True).status_code == 200
    assert b"tiny star" not in client.get(f"/items/{item_id}").data
    assert b"tiny star" in client.get("/review/claims").data
    assert client.post("/review/claims/1", data={"csrf_token": csrf, "action": "approve"}, follow_redirects=True).status_code == 200
    assert store.get_item(item_id)["status"] == "Returned"
    assert [claim["status"] for claim in store.list_claims()] == ["Rejected", "Approved"]
    assert client.post("/review/claims/2", data={"csrf_token": csrf, "action": "approve"}).status_code == 302
    assert store.get_item(item_id)["status"] == "Returned"
    assert client.get(f"/items/{item_id}/claim").status_code == 404


def test_bad_input_and_csrf_rejected():
    client, store = client_and_store()
    csrf = token(client)
    assert client.post("/items/new", data={"csrf_token": "wrong"}).status_code == 400
    assert client.post("/items/new", data=dict(csrf_token=csrf, kind="Lost", title="Future item",
        description="A made up item description", category="Other", location="Library",
        report_date="2999-01-01")).status_code == 200
    assert len(store.list_items()) == 6
    assert client.post("/items/2/claim", data=dict(csrf_token=csrf, name="A",
        contact="not-an-email", explanation="too short")).status_code == 200
    assert store.list_claims() == []
