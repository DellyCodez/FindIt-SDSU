"""Actual image upload, processing, gallery, and migration checks."""

from contextlib import closing
from datetime import date
from io import BytesIO
import sqlite3

from PIL import Image
import pytest

from app import create_app
from app.init_db import initialize_database
from app.storage import SQLiteStore, connect


def picture(format="PNG", color="red"):
    stream = BytesIO()
    Image.new("RGB", (80, 60), color).save(stream, format=format)
    stream.seek(0)
    return stream


def form(csrf, files):
    return dict(csrf_token=csrf, kind="Found", title="Fictional red bottle",
                description="A red bottle with a small crescent sticker.",
                category="Drinkware", item_type="Water Bottle", location="Library", report_date=date.today().isoformat(),
                photos=files)


def setup(tmp_path):
    path = initialize_database(tmp_path / "demo.sqlite3")
    store = SQLiteStore(path)
    client = create_app(store).test_client()
    client.get("/")
    with client.session_transaction() as session:
        csrf = session["csrf_token"]
    return store, client, csrf


def test_three_supported_photo_formats_are_reencoded_shown_and_persist(tmp_path):
    store, client, csrf = setup(tmp_path)
    response = client.post("/items/new", data=form(csrf, [
        (picture("PNG"), "front.png"), (picture("JPEG"), "back.jpg"),
        (picture("WEBP"), "detail.webp")]),
        content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    item = store.list_items({"q": "Fictional red bottle"})[0]
    photos = store.list_photos(item["id"])
    assert len(photos) == 3 and item["photo_id"] == photos[0]["id"]
    assert item["item_type"] == "Water Bottle"
    assert b"gallery-thumb" in response.data
    for photo in photos:
        delivered = client.get(f"/photos/{photo['id']}")
        assert delivered.status_code == 200
        assert delivered.content_type == "image/webp"
        assert delivered.headers["X-Content-Type-Options"] == "nosniff"
        with Image.open(BytesIO(delivered.data)) as image:
            assert image.format == "WEBP" and image.size == (80, 60)
            assert not image.getexif()
    assert client.get("/photos/999999").status_code == 404
    assert f"/photos/{photos[0]['id']}".encode() in client.get("/items").data
    restarted = SQLiteStore(store.path)
    assert len(restarted.list_photos(item["id"])) == 3
    assert create_app(restarted).test_client().get(f"/photos/{photos[1]['id']}").status_code == 200
    assert len(list(store.upload_dir.glob("*.webp"))) == 3


def test_bad_photos_do_not_create_reports_or_files(tmp_path):
    store, client, csrf = setup(tmp_path)
    bad_inputs = [
        [(BytesIO(b"not a picture"), "malware.exe")],
        [(BytesIO(b"not a picture"), "fake.png")],
        [(picture("PNG"), "wrong.jpg")],
        [(BytesIO(b"x" * (5 * 1024 * 1024 + 1)), "huge.jpg")],
        [(picture(), f"photo-{number}.png") for number in range(4)],
    ]
    for files in bad_inputs:
        response = client.post("/items/new", data=form(csrf, files),
                               content_type="multipart/form-data")
        assert response.status_code == 200
        assert b'"photos-error"' in response.data
        assert len(store.list_items()) == 6
        assert not list(store.upload_dir.glob("*.webp"))


def test_photo_relationship_constraints_and_repeatable_setup(tmp_path):
    store, _, _ = setup(tmp_path)
    initialize_database(store.path)
    with closing(connect(store.path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 6
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO item_photos(item_id,file_name,position,mime_type,width,height,byte_count)
                VALUES(99999,?,?,?,?,?,?)
            """, ("a" * 32 + ".webp", 1, "image/webp", 80, 60, 100))
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("""
                INSERT INTO item_photos(item_id,file_name,position,mime_type,width,height,byte_count)
                VALUES(1,?,?,?,?,?,?)
            """, ("b" * 32 + ".webp", 4, "image/webp", 80, 60, 100))


def test_v4_upgrade_preserves_uploaded_photos_and_claims(tmp_path):
    store, client, csrf = setup(tmp_path)
    client.post("/items/new", data=form(csrf, [(picture(), "bottle.png")]),
                content_type="multipart/form-data")
    item = store.list_items({"q": "Fictional red bottle"})[0]
    store.submit_claim(item["id"], dict(name="Fictional Student", contact="student@example.test",
                                        explanation="A small scratch is hidden under its lid."))
    before_photos = store.list_photos(item["id"])
    with closing(connect(store.path)) as connection:
        before_claims = [tuple(row) for row in connection.execute("SELECT * FROM claims ORDER BY id")]
        connection.execute("ALTER TABLE items DROP COLUMN contact_email")
        connection.execute("ALTER TABLE items DROP COLUMN distinguishing_features")
        connection.execute("PRAGMA user_version = 4")
    initialize_database(store.path)
    upgraded = SQLiteStore(store.path)
    assert upgraded.list_photos(item["id"]) == before_photos
    assert (upgraded.upload_dir / upgraded.get_photo(before_photos[0]["id"])["file_name"]).is_file()
    with closing(connect(store.path)) as connection:
        assert [tuple(row) for row in connection.execute("SELECT * FROM claims ORDER BY id")] == before_claims
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    initialize_database(store.path)
    assert len(upgraded.list_photos(item["id"])) == 1
