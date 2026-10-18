"""Structured reports, conservative matching, privacy, and end-to-end claim checks."""

from datetime import date, timedelta
from io import BytesIO
import sqlite3

from PIL import Image
import pytest

from app import create_app
from app.init_db import initialize_database
from app.matching import possible_matches, same_model
from app.storage import SQLiteStore, connect


TODAY = date.today()


def setup(tmp_path):
    path = initialize_database(tmp_path / "stage2.sqlite3")
    store = SQLiteStore(path)
    client = create_app(store).test_client()
    client.get("/items/new")
    with client.session_transaction() as session:
        csrf = session["csrf_token"]
    return path, store, client, csrf


def item(store, kind, item_type, title, description, *, category="Electronics",
         color="Black", brand=None, model=None, location="Library", days=0, features=None):
    return store.create_item({
        "kind": kind, "title": title, "description": description,
        "category": category, "location": location, "report_date": (TODAY + timedelta(days=days)).isoformat(),
        "item_type": item_type, "primary_color": color, "brand": brand,
        "model": model, "distinguishing_features": features,
    })


def ids(store, source):
    return [match["item"]["id"] for match in possible_matches(store, source, limit=20)]


def test_phone_vs_phone_earbuds_color_generic_words_and_missing_brand(tmp_path):
    assert same_model("iphone 14 pro max", "14 pro max")
    assert not same_model("galaxy s23", "pixel s23")
    _, store, _, _ = setup(tmp_path)
    lost = item(store, "Lost", "Smartphone", "iPhone 14 Pro Max",
                "Black phone with a silver star sticker under the case.",
                brand="Apple", model="iPhone 14 Pro Max", features="Silver star sticker")
    same = item(store, "Found", "Smartphone", "iPhone 14 Pro Max",
                "Black phone with a silver star sticker.",
                brand="Apple", model="iPhone 14 Pro Max")
    earbuds = item(store, "Found", "Earbuds", "Wireless earbuds",
                    "Black earbuds in a case with a silver star sticker.")
    wrong_color = item(store, "Found", "Smartphone", "iPhone 14 Pro Max",
                       "Blue phone with a silver star sticker.",
                       color="Blue", brand="Apple", model="iPhone 14 Pro Max")
    unrelated = item(store, "Found", "Smartphone", "Galaxy phone",
                     "Black phone in a case near the library.")
    no_brand = item(store, "Found", "Smartphone", "Black phone with star",
                    "A black phone with a silver star sticker and no visible model.")
    short_model = item(store, "Found", "Smartphone", "Black iPhone with star",
                       "Black phone with a silver star sticker.", brand="Apple", model="14 Pro Max")
    different_model = item(store, "Found", "Smartphone", "Black iPhone with star",
                           "Black phone with a silver star sticker.", brand="Apple", model="iPhone 14 Pro")
    suggestions = ids(store, lost)
    assert same["id"] in suggestions
    assert no_brand["id"] in suggestions
    assert short_model["id"] in suggestions
    assert different_model["id"] not in suggestions
    assert earbuds["id"] not in suggestions
    assert wrong_color["id"] not in suggestions
    assert unrelated["id"] not in suggestions
    assert ids(store, earbuds) == []
    assert all("case" not in " ".join(m["reasons"]).lower() for m in possible_matches(store, lost))


def test_water_bottle_legacy_fallback_and_date_boundaries(tmp_path):
    _, store, _, _ = setup(tmp_path)
    lost = item(store, "Lost", "Water Bottle", "Red water bottle",
                "Matte bottle with a moon sticker near the lid.",
                category="Drinkware", color="Red", days=-50)
    within = item(store, "Found", "Water Bottle", "Red water bottle",
                  "Matte bottle with a moon sticker near the lid.",
                  category="Drinkware", color="Red", days=-5)
    too_late = item(store, "Found", "Water Bottle", "Red water bottle",
                    "Matte bottle with a moon sticker near the lid.",
                    category="Drinkware", color="Red", days=-4)
    early = item(store, "Found", "Water Bottle", "Red water bottle",
                 "Matte bottle with a moon sticker near the lid.",
                 category="Drinkware", color="Red", days=-52)
    too_early = item(store, "Found", "Water Bottle", "Red water bottle",
                     "Matte bottle with a moon sticker near the lid.",
                     category="Drinkware", color="Red", days=-53)
    assert within["id"] in ids(store, lost)
    assert early["id"] in ids(store, lost)
    assert too_late["id"] not in ids(store, lost)
    assert too_early["id"] not in ids(store, lost)
    # Old reports have no invented attributes; the title can still identify an obvious type.
    legacy = store.create_item(dict(kind="Found", title="Red water bottle",
        description="Matte bottle with a moon sticker near the lid.",
        category="Drinkware", location="Library", report_date=(TODAY - timedelta(days=49)).isoformat()))
    assert store.get_item(legacy["id"])["item_type"] is None
    assert legacy["id"] in ids(store, lost)


def test_form_categories_privacy_and_duplicate_claim(tmp_path):
    _, store, client, csrf = setup(tmp_path)
    fields = dict(csrf_token=csrf, kind="Found", title="Black phone with a star",
                  description="A black phone with a silver star sticker on its back.",
                  category="Electronics", item_type="Smartphone", primary_color="Black",
                  location="Library", report_date=TODAY.isoformat())
    form = client.get("/items/new").data
    assert b'data-category="Electronics"' in form and b'data-category="Drinkware"' in form
    assert b'name="brand"' in form and b'name="distinguishing_features"' in form
    for changes, message in [
        ({"item_type": "Earbuds", "category": "Drinkware"}, b"Choose an item type"),
        ({"item_type": ""}, b"Choose an item type"),
        ({"description": "Email me at student@example.test about this black phone."}, b"Remove email addresses"),
        ({"description": "Call 619-555-0199 about this black phone."}, b"Remove email addresses"),
        ({"title": "student@example.test phone"}, b"Remove email addresses"),
    ]:
        page = client.post("/items/new", data={**fields, **changes})
        assert message in page.data
        assert len(store.list_items()) == 6
    assert client.post("/items/new", data=fields).status_code == 302
    found = store.list_items({"q": "Black phone with a star"})[0]
    claim = dict(csrf_token=csrf, name="Fictional Student", contact="student@example.test",
                 explanation="There is a hidden star sticker beneath the case.")
    assert client.post(f"/items/{found['id']}/claim", data=claim).status_code == 302
    duplicate = client.post(f"/items/{found['id']}/claim", data=claim)
    assert duplicate.status_code == 409
    assert b"already recorded" in duplicate.data
    assert len(store.list_claims()) == 1
    public = client.get(f"/items/{found['id']}").data
    assert b"student@example.test" not in public
    assert claim["explanation"].encode() not in public
    assert b"student@example.test" in client.get("/review/claims").data
    assert client.get("/review/claims", environ_overrides={"REMOTE_ADDR": "203.0.113.9"}).status_code == 403


def test_structured_schema_checks_and_restart(tmp_path):
    path, store, _, _ = setup(tmp_path)
    found = item(store, "Found", "Smartphone", "Black iPhone",
                 "Black iPhone with silver star sticker.", brand="Apple",
                 model="iPhone 14 Pro Max", features="Silver star sticker")
    assert SQLiteStore(path).get_item(found["id"])["model"] == "iPhone 14 Pro Max"
    with connect(path) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE items SET primary_color = '' WHERE id = ?", (found["id"],))
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE items SET category_id = 99999 WHERE id = ?", (found["id"],))
    initialize_database(path)
    assert SQLiteStore(path).get_item(found["id"])["item_type"] == "Smartphone"


def image_bytes(color):
    out = BytesIO()
    Image.new("RGB", (80, 80), color).save(out, "PNG")
    out.seek(0)
    return out


def test_full_photo_match_claim_approval_restart(tmp_path):
    path, store, client, csrf = setup(tmp_path)
    lost = dict(csrf_token=csrf, kind="Lost", title="Black iPhone with star",
                description="Black iPhone with a silver star sticker on the back.",
                category="Electronics", item_type="Smartphone", brand="Apple",
                model="iPhone 14 Pro Max", primary_color="Black", location="Library",
                report_date=(TODAY - timedelta(days=1)).isoformat(),
                photos=[(image_bytes(c), f"{c}.png") for c in ("red", "green", "blue")])
    assert client.post("/items/new", data=lost, content_type="multipart/form-data").status_code == 302
    lost_id = store.list_items({"q": "Black iPhone with star"})[0]["id"]
    found = {**lost, "kind": "Found", "title": "Found black iPhone with star",
             "photos": [(image_bytes("purple"), "found.png")],
             "report_date": TODAY.isoformat()}
    assert client.post("/items/new", data=found, content_type="multipart/form-data").status_code == 302
    found_id = store.list_items({"q": "Found black iPhone"})[0]["id"]
    assert found_id in ids(store, store.get_item(lost_id))
    assert len(store.get_photos(lost_id)) == 3
    detail = client.get(f"/items/{lost_id}").data
    assert b"Similarity" in detail and b"Same model" in detail
    for photo in store.get_photos(lost_id):
        assert client.get(f"/items/{lost_id}/photos/{photo['id']}").status_code == 200
    claim = dict(csrf_token=csrf, name="Demo One", contact="one@example.test",
                 explanation="The hidden star sticker has a tiny scratch.")
    second = {**claim, "name": "Demo Two", "contact": "two@example.test"}
    assert client.post(f"/items/{found_id}/claim", data=claim).status_code == 302
    assert client.post(f"/items/{found_id}/claim", data=second).status_code == 302
    claims = store.list_claims()
    assert b"review-image" in client.get("/review/claims").data
    assert client.post(f"/review/claims/{claims[1]['id']}", data={"csrf_token": csrf, "action": "approve"}).status_code == 302
    assert not store.review_claim(claims[0]["id"], "approve")
    restarted = SQLiteStore(path)
    assert restarted.get_item(found_id)["status"] == "Returned"
    assert [c["status"] for c in restarted.list_claims()] == ["Rejected", "Approved"]
    assert found_id not in ids(restarted, restarted.get_item(lost_id))
    assert len(restarted.get_photos(lost_id)) == 3
    new_client = create_app(restarted).test_client()
    assert new_client.get(f"/items/{lost_id}").status_code == 200
    assert new_client.get(f"/items/{lost_id}/photos/{restarted.get_photos(lost_id)[0]['id']}").status_code == 200
    assert claim["explanation"].encode() not in new_client.get(f"/items/{found_id}").data
