"""Published v4 compatibility, presenter access, and a protected end-to-end journey."""

from contextlib import closing
from datetime import date, timedelta
from io import BytesIO
import sqlite3

from PIL import Image
import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.init_db import initialize_database
from app.matching import possible_matches, same_model
from app.storage import SQLiteStore, connect


PUBLIC_ORIGIN = "https://localhost"


def image_bytes(color):
    stream = BytesIO()
    Image.new("RGB", (80, 80), color).save(stream, "PNG")
    stream.seek(0)
    return stream


def csrf_token(client):
    with client.session_transaction() as session:
        return session["csrf_token"]


def report_data(csrf, kind, **changes):
    values = dict(csrf_token=csrf, kind=kind, title="Matte red bottle with crescent sticker",
                  description="Matte red bottle with black loop lid and pale crescent sticker near its base.",
                  category="Drinkware", item_type="Water Bottle", location="Library",
                  report_date=date.today().isoformat(), brand="Sierra Bottle", model="Trail 32",
                  color="Red", contact_email=f"{kind.lower()}-reporter@example.test")
    return {**values, **changes}


# ==============================================================================
# SECTION: SCHEMA EVOLUTION & MIGRATIONS
# ==============================================================================

# Migration: verifies upgrading v4 database preserves photo metadata, claims, and column renames.
def test_published_v4_layout_migrates_without_losing_photos_or_claims(tmp_path):
    path = initialize_database(tmp_path / "published-v4.sqlite3")
    store = SQLiteStore(path)
    encoded = BytesIO()
    Image.new("RGB", (80, 80), "red").save(encoded, "WEBP")
    data = report_data("", "Found")
    created = store.create_item(data, [dict(data=encoded.getvalue(), mime_type="image/webp",
                                            width=80, height=80, byte_count=len(encoded.getvalue()))])
    claim = store.submit_claim(created["id"], dict(name="Fictional Owner", contact="owner@example.test",
                                                   explanation="A hidden scratch is under the black lid."))
    photo = store.list_photos(created["id"])[0]
    with closing(connect(path)) as connection:
        connection.execute("ALTER TABLE items ADD COLUMN primary_color TEXT")
        connection.execute("UPDATE items SET primary_color = color WHERE id = ?", (created["id"],))
        connection.execute("ALTER TABLE items DROP COLUMN color")
        connection.execute("ALTER TABLE items DROP COLUMN contact_email")
        connection.execute("DROP INDEX idx_items_match_type")
        connection.execute("ALTER TABLE item_photos RENAME COLUMN file_name TO filename")
        connection.execute("ALTER TABLE item_photos RENAME COLUMN byte_count TO byte_size")
        connection.execute("ALTER TABLE item_photos DROP COLUMN mime_type")
        connection.execute("PRAGMA user_version = 4")
        before = {table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY id")]
                  for table in ("users", "categories", "locations", "claims")}
    initialize_database(path)
    upgraded = SQLiteStore(path)
    assert upgraded.get_item(created["id"])["color"] == "Red"
    assert upgraded.get_item(created["id"])["model"] == "Trail 32"
    assert upgraded.get_photo(photo["id"])["mime_type"] == "image/webp"
    assert (upgraded.upload_dir / upgraded.get_photo(photo["id"])["file_name"]).is_file()
    assert upgraded.list_claims()[0]["id"] == claim["id"]
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 8
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert {table: [tuple(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY id")]
                for table in before} == before
    initialize_database(path)
    assert len(SQLiteStore(path).list_photos(created["id"])) == 1


# Migration: verifies upgrading v6 database restores submission attempts table without affecting existing rows.
def test_version_six_migration_preserves_reports_and_claims(tmp_path):
    path = initialize_database(tmp_path / "version-six.sqlite3")
    store = SQLiteStore(path)
    created = store.create_item(report_data("", "Found"))
    store.submit_claim(created["id"], dict(name="Fictional Owner", contact="owner@example.test",
                                           explanation="The underside has a tiny painted star."))
    with closing(connect(path)) as connection:
        before = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                  for table in ("users", "categories", "locations", "items", "item_photos", "claims")}
        connection.execute("DROP TABLE submission_attempts")
        connection.execute("PRAGMA user_version = 6")
    initialize_database(path)
    initialize_database(path)
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 8
        assert {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in before} == before
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("SELECT COUNT(*) FROM submission_attempts").fetchone()[0] == 0


# Migration: verifies upgrading v7 database applies report visibility column and indexes cleanly.
def test_version_seven_migration_preserves_claims_and_visibility_defaults(tmp_path):
    path = initialize_database(tmp_path / "version-seven.sqlite3")
    store = SQLiteStore(path)
    item = store.create_item(report_data("", "Found"))
    store.submit_claim(item["id"], dict(name="Fictional Owner", contact="owner@example.test",
                                         explanation="A tiny painted star is underneath."))
    with closing(connect(path)) as connection:
        before = [tuple(row) for row in connection.execute("SELECT * FROM claims")]
        connection.execute("DROP INDEX idx_items_visibility_date")
        connection.execute("ALTER TABLE items DROP COLUMN visibility")
        connection.execute("PRAGMA user_version = 7")
    initialize_database(path)
    initialize_database(path)
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 8
        assert [tuple(row) for row in connection.execute("SELECT * FROM claims")] == before
        assert connection.execute("SELECT visibility FROM items WHERE id = ?", (item["id"],)).fetchone()[0] == "Visible"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


# ==============================================================================
# SECTION: AUTHENTICATION & ACCESS CONTROL
# ==============================================================================

# Security: verifies that public mode enforces SECRET_KEY, protects /admin routes, and requires valid login passwords.
def test_public_mode_requires_secrets_and_keeps_admin_private(tmp_path, monkeypatch):
    path = initialize_database(tmp_path / "protected.sqlite3")
    monkeypatch.setenv("FINDIT_PUBLIC", "1")
    monkeypatch.setenv("FINDIT_ALLOWED_HOSTS", "localhost")
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("PRESENTER_PASSWORD_HASH", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app(SQLiteStore(path))
    monkeypatch.setenv("SECRET_KEY", "fictional-test-secret-only")
    monkeypatch.setenv("PRESENTER_PASSWORD_HASH", generate_password_hash("correct fictional password"))
    client = create_app(SQLiteStore(path)).test_client()
    for route in ("/", "/items", "/items/1", "/about", "/product", "/blog", "/resources",
                  "/items/new", "/items/2/claim"):
        assert client.get(route, base_url=PUBLIC_ORIGIN).status_code == 200
    response = client.get("/admin/claims", base_url=PUBLIC_ORIGIN)
    assert response.status_code == 302 and "/admin/login" in response.location
    assert client.post("/admin/claims/1", base_url=PUBLIC_ORIGIN).status_code == 403
    assert b"Admin sign in" not in client.get("/", base_url=PUBLIC_ORIGIN).data
    assert client.post("/items/new", base_url=PUBLIC_ORIGIN,
                       data=report_data("wrong", "Found")).status_code == 400
    assert b"fictional-test-secret-only" not in client.get("/", base_url=PUBLIC_ORIGIN).data
    login = client.get("/admin/login", base_url=PUBLIC_ORIGIN)
    assert login.status_code == 200
    wrong = client.post("/admin/login", base_url=PUBLIC_ORIGIN, data={
        "csrf_token": csrf_token(client), "password": "wrong"})
    assert wrong.status_code == 200 and b"not recognized" in wrong.data
    correct = client.post("/admin/login", base_url=PUBLIC_ORIGIN, data={
        "csrf_token": csrf_token(client), "password": "correct fictional password"})
    assert correct.status_code == 302 and correct.location.endswith("/admin/claims")
    assert client.get("/admin/claims", base_url=PUBLIC_ORIGIN).status_code == 200
    assert client.get("/admin/claims", base_url=PUBLIC_ORIGIN).headers["Cache-Control"] == "no-store"
    token = csrf_token(client)
    assert client.post("/presenter/logout", base_url=PUBLIC_ORIGIN, data={"csrf_token": token}).status_code == 302
    assert client.get("/admin/claims", base_url=PUBLIC_ORIGIN).status_code == 302
    assert client.get("/items", base_url="https://untrusted.example").status_code == 400


# ==============================================================================
# SECTION: END-TO-END WORKFLOW & RESTART INTEGRITY
# ==============================================================================

# Workflow: verifies full end-to-end lifecycle under public security mode across app and database restarts.
def test_public_photo_match_claim_and_admin_approval_survive_restart(tmp_path, monkeypatch):
    path = initialize_database(tmp_path / "journey.sqlite3")
    monkeypatch.setenv("FINDIT_PUBLIC", "1")
    monkeypatch.setenv("FINDIT_ALLOWED_HOSTS", "localhost")
    monkeypatch.setenv("SECRET_KEY", "fictional-test-secret-only")
    monkeypatch.setenv("PRESENTER_PASSWORD_HASH", generate_password_hash("correct fictional password"))
    client = create_app(SQLiteStore(path)).test_client()
    assert client.get("/items/new", base_url=PUBLIC_ORIGIN).status_code == 200
    token = csrf_token(client)
    lost = client.post("/items/new", base_url=PUBLIC_ORIGIN, data=report_data(token, "Lost",
        report_date=(date.today() - timedelta(days=1)).isoformat()))
    assert lost.status_code == 302
    found_form = report_data(token, "Found")
    found_form["photos"] = [(image_bytes("red"), "front.png"), (image_bytes("blue"), "back.png")]
    found = client.post("/items/new", base_url=PUBLIC_ORIGIN, data=found_form,
                        content_type="multipart/form-data")
    assert found.status_code == 302
    store = SQLiteStore(path)
    lost_id, found_id = [row["id"] for row in store.list_items({"q": "crescent sticker", "sort": "oldest"})][-2:]
    assert found_id in [match["item"]["id"] for match in possible_matches(store, store.get_item(lost_id))]
    photos = store.list_photos(found_id)
    assert len(photos) == 2
    for photo in photos:
        assert client.get(f"/photos/{photo['id']}", base_url=PUBLIC_ORIGIN).status_code == 200
    assert b"found-reporter@example.test" not in client.get(f"/items/{found_id}", base_url=PUBLIC_ORIGIN).data
    claim = client.post(f"/items/{found_id}/claim", base_url=PUBLIC_ORIGIN, data={
        "csrf_token": token, "name": "Fictional Owner", "contact": "owner@example.test",
        "explanation": "A hidden scratch is under the black loop lid."})
    assert claim.status_code == 302 and claim.location.endswith("/claim/received")
    assert b"Claim received" in client.get(claim.location, base_url=PUBLIC_ORIGIN).data
    visitor = create_app(SQLiteStore(path)).test_client()
    assert visitor.get("/admin/claims", base_url=PUBLIC_ORIGIN).status_code == 302
    public_detail = visitor.get(f"/items/{found_id}", base_url=PUBLIC_ORIGIN).data
    assert b"owner@example.test" not in public_detail
    assert b"hidden scratch" not in public_detail
    client.get("/admin/login", base_url=PUBLIC_ORIGIN)
    client.post("/admin/login", base_url=PUBLIC_ORIGIN, data={
        "csrf_token": csrf_token(client), "password": "correct fictional password"})
    review = client.get("/admin/claims", base_url=PUBLIC_ORIGIN)
    assert b"found-reporter@example.test" in review.data
    claim_id = store.list_claims()[0]["id"]
    approved = client.post(f"/admin/claims/{claim_id}", base_url=PUBLIC_ORIGIN,
                           data={"csrf_token": csrf_token(client), "action": "approve"})
    assert approved.status_code == 302
    restarted = SQLiteStore(path)
    assert restarted.get_item(found_id)["status"] == "Returned"
    assert len(restarted.list_photos(found_id)) == 2
    assert restarted.list_claims()[0]["status"] == "Approved"
    assert client.get(f"/items/{found_id}", base_url=PUBLIC_ORIGIN).status_code == 200
    assert f'/items/{found_id}"'.encode() not in client.get("/", base_url=PUBLIC_ORIGIN).data


# ==============================================================================
# SECTION: INPUT SANITIZATION & BOUNDARY VALIDATION
# ==============================================================================

# Boundary: verifies fuzzy model normalization and rejects exposed email/phone patterns in public fields.
def test_model_normalization_and_public_field_validation(tmp_path):
    assert same_model("iPhone 14 Pro Max", "14 Pro Max")
    assert not same_model("Galaxy S23", "Pixel S23")
    path = initialize_database(tmp_path / "public-fields.sqlite3")
    client = create_app(SQLiteStore(path)).test_client()
    client.get("/items/new")
    token = csrf_token(client)
    for field, value in (("title", "Call 619-555-0199"),
                         ("description", "Email student@example.test about this item."),
                         ("brand", "student@example.test")):
        response = client.post("/items/new", data=report_data(token, "Found", **{field: value}))
        assert response.status_code == 200
        assert b"email addresses and phone numbers" in response.data
    assert len(SQLiteStore(path).list_items()) == 6


# ==============================================================================
# SECTION: NETWORKING & RATE LIMITING
# ==============================================================================

# Networking: verifies rolling window rate limiting (HTTP 429) across separate app instances and bot honeypots.
def test_public_forms_reject_bots_and_limit_attempts_across_app_instances(tmp_path, monkeypatch):
    path = initialize_database(tmp_path / "limits.sqlite3")
    monkeypatch.setenv("FINDIT_PUBLIC", "1")
    monkeypatch.setenv("FINDIT_ALLOWED_HOSTS", "localhost")
    monkeypatch.setenv("SECRET_KEY", "stable-fictional-rate-limit-key")
    monkeypatch.setenv("PRESENTER_PASSWORD_HASH", generate_password_hash("correct fictional password"))
    client = create_app(SQLiteStore(path)).test_client()
    client.get("/items/new", base_url=PUBLIC_ORIGIN)
    token = csrf_token(client)
    assert client.post("/items/new", base_url=PUBLIC_ORIGIN,
                       data=report_data("wrong", "Found")).status_code == 400
    assert client.post("/items/new", base_url=PUBLIC_ORIGIN,
                       data=report_data(token, "Found", website="spam.example")).status_code == 400
    for _ in range(4):
        invalid = client.post("/items/new", base_url=PUBLIC_ORIGIN,
                              data=report_data(token, "Found", title="Bad"))
        assert invalid.status_code == 200
    assert client.post("/items/new", base_url=PUBLIC_ORIGIN,
                       data=report_data(token, "Found")).status_code == 429
    other_app = create_app(SQLiteStore(path)).test_client()
    other_app.get("/items/new", base_url=PUBLIC_ORIGIN)
    assert other_app.post("/items/new", base_url=PUBLIC_ORIGIN,
                          data=report_data(csrf_token(other_app), "Found")).status_code == 429
    with closing(connect(path)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM submission_attempts").fetchone()[0] == 4
        assert "127.0.0.1" not in str(connection.execute(
            "SELECT actor_key FROM submission_attempts").fetchall())
    assert len(SQLiteStore(path).list_items()) == 6


# ==============================================================================
# SECTION: MODERATION & CONTENT PRIVACY
# ==============================================================================

# Moderation: verifies that an admin can toggle item visibility to hide reports, photos, and match results from public views.
def test_admin_moderation_hides_reports_photos_and_matches(tmp_path, monkeypatch):
    path = initialize_database(tmp_path / "moderation.sqlite3")
    store = SQLiteStore(path)
    data = report_data("", "Found")
    encoded = BytesIO()
    Image.new("RGB", (80, 80), "red").save(encoded, "WEBP")
    item = store.create_item(data, [dict(data=encoded.getvalue(), mime_type="image/webp",
                                         width=80, height=80, byte_count=len(encoded.getvalue()))])
    photo_id = store.list_photos(item["id"])[0]["id"]
    monkeypatch.setenv("FINDIT_PUBLIC", "1")
    monkeypatch.setenv("FINDIT_ALLOWED_HOSTS", "localhost")
    monkeypatch.setenv("SECRET_KEY", "fictional-moderation-test-key")
    monkeypatch.setenv("PRESENTER_PASSWORD_HASH", generate_password_hash("correct fictional password"))
    visitor = create_app(store).test_client()
    admin = create_app(store).test_client()
    assert visitor.get("/admin/items", base_url=PUBLIC_ORIGIN).status_code == 302
    assert visitor.post(f"/admin/items/{item['id']}/visibility", base_url=PUBLIC_ORIGIN,
                        data={"visibility": "Hidden"}).status_code == 403
    admin.get("/admin/login", base_url=PUBLIC_ORIGIN)
    admin.post("/admin/login", base_url=PUBLIC_ORIGIN, data={
        "csrf_token": csrf_token(admin), "password": "correct fictional password"})
    admin.get("/admin/items", base_url=PUBLIC_ORIGIN)
    assert admin.post(f"/admin/items/{item['id']}/visibility", base_url=PUBLIC_ORIGIN,
                      data={"csrf_token": csrf_token(admin), "visibility": "Hidden"}).status_code == 302
    assert store.get_item(item["id"]) is None
    assert item["id"] not in [row["id"] for row in store.list_items()]
    assert visitor.get(f"/items/{item['id']}", base_url=PUBLIC_ORIGIN).status_code == 404
    assert visitor.get(f"/photos/{photo_id}", base_url=PUBLIC_ORIGIN).status_code == 404
    assert visitor.get(f"/items/{item['id']}/claim", base_url=PUBLIC_ORIGIN).status_code == 404
    assert not any(match["item"]["id"] == item["id"] for match in
                   possible_matches(store, store.get_item(1)))
    assert admin.post(f"/admin/items/{item['id']}/visibility", base_url=PUBLIC_ORIGIN,
                      data={"csrf_token": csrf_token(admin), "visibility": "Visible"}).status_code == 302
    assert visitor.get(f"/items/{item['id']}", base_url=PUBLIC_ORIGIN).status_code == 200
    assert visitor.get(f"/photos/{photo_id}", base_url=PUBLIC_ORIGIN).status_code == 200
