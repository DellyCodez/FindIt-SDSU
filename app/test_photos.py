"""Photo upload, display, safety, and in-place migration checks."""

from contextlib import closing
from datetime import date
from hashlib import sha256
from io import BytesIO
import sqlite3

from PIL import Image
import pytest

from app import create_app
from app.init_db import initialize_database
from app.storage import SQLiteStore, connect


def image_file(format_name, color="navy", size=(120, 90), exif=None):
    output = BytesIO()
    image = Image.new("RGB", size, color)
    options = {"exif": exif} if exif else {}
    image.save(output, format=format_name, **options)
    output.seek(0)
    return output


def setup(tmp_path):
    path = initialize_database(tmp_path / "findit.sqlite3")
    store = SQLiteStore(path)
    client = create_app(store).test_client()
    client.get("/items/new")
    with client.session_transaction() as session:
        csrf = session["csrf_token"]
    report = dict(csrf_token=csrf, kind="Lost", title="Black smartphone",
                  description="Black smartphone with a small silver sticker.",
                  category="Electronics", location="Library",
                  report_date=date.today().isoformat())
    return client, store, path, report


def test_three_formats_gallery_cards_metadata_and_restart(tmp_path):
    client, store, path, report = setup(tmp_path)
    exif = Image.Exif()
    exif[270] = "private camera note"
    response = client.post("/items/new", data={**report, "photos": [
        (image_file("JPEG", color="red", exif=exif), "front.jpg"),
        (image_file("PNG", color="green"), "back.png"),
        (image_file("WEBP", color="blue"), "case.webp"),
    ]}, content_type="multipart/form-data", follow_redirects=True)
    assert response.status_code == 200
    assert b"gallery-thumb" in response.data
    item = store.list_items({"q": "Black smartphone"})[0]
    photos = store.get_photos(item["id"])
    assert len(photos) == 3
    assert [photo["position"] for photo in photos] == [1, 2, 3]
    assert item["photo_id"] == photos[0]["id"]
    stored_files = list(store.upload_dir.iterdir())
    assert len(stored_files) == 3
    assert all(file.name.endswith(".webp") and len(file.stem) == 32 for file in stored_files)
    assert all(file.name not in {"front.jpg", "back.png", "case.webp"} for file in stored_files)
    assert all(file.stat().st_mode & 0o777 == 0o600 for file in stored_files)
    assert f'/items/{item["id"]}/photos/{photos[0]["id"]}'.encode() in client.get("/").data
    assert f'/items/{item["id"]}/photos/{photos[0]["id"]}'.encode() in client.get("/items").data
    hashes = []
    for index, photo in enumerate(photos):
        photo_url = f'/items/{item["id"]}/photos/{photo["id"]}'
        assert photo_url.encode() in response.data
        result = client.get(photo_url)
        assert result.status_code == 200
        assert result.mimetype == "image/webp"
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        with Image.open(BytesIO(result.data)) as decoded:
            assert decoded.format == "WEBP"
            assert decoded.size == (photo["width"], photo["height"])
            assert not decoded.getexif()
            pixel = decoded.convert("RGB").getpixel((10, 10))
            assert pixel[index] > max(pixel[channel] for channel in range(3) if channel != index) + 40
        assert len(result.data) == photo["byte_size"]
        hashes.append(sha256(result.data).hexdigest())
    assert len(set(hashes)) == 3
    assert client.get(f'/items/1/photos/{photos[0]["id"]}').status_code == 404
    assert client.get(f'/items/{item["id"]}/photos/99999').status_code == 404
    restarted = SQLiteStore(path)
    assert restarted.get_photos(item["id"]) == photos
    assert create_app(restarted).test_client().get(
        f'/items/{item["id"]}/photos/{photos[0]["id"]}').status_code == 200


@pytest.mark.parametrize("filename,content,message", [
    ("script.php", lambda: BytesIO(b"<?php echo 1; ?>"), b"JPEG, PNG, or WebP"),
    ("fake.png", lambda: image_file("JPEG"), b"invalid or unsupported"),
    ("broken.jpg", lambda: BytesIO(b"not a jpeg"), b"valid image"),
    ("huge.jpg", lambda: BytesIO(b"x" * (8 * 1024 * 1024 + 1)), b"8 MB"),
])
def test_invalid_files_do_not_create_report_or_photo(tmp_path, filename, content, message):
    client, store, _, report = setup(tmp_path)
    response = client.post("/items/new", data={**report, "photos": (content(), filename)},
                           content_type="multipart/form-data")
    assert response.status_code == 200
    assert message in response.data
    assert len(store.list_items()) == 6
    assert not store.upload_dir.exists()


def test_photo_limit_and_no_photo_phone_illustration(tmp_path):
    client, store, _, report = setup(tmp_path)
    response = client.post("/items/new", data={**report, "photos": [
        (image_file("PNG"), f"{number}.png") for number in range(4)
    ]}, content_type="multipart/form-data")
    assert b"no more than three" in response.data
    assert len(store.list_items()) == 6
    assert not store.upload_dir.exists()
    response = client.post("/items/new", data=report, follow_redirects=True)
    assert response.status_code == 200
    assert b'width="46" height="96"' in response.data  # phone, not headphones
    assert b"Illustration" in response.data


def test_excessive_pixel_dimensions_are_rejected(tmp_path):
    client, store, _, report = setup(tmp_path)
    response = client.post("/items/new", data={**report, "photos": (
        image_file("PNG", size=(5000, 5000)), "huge-pixels.png")},
        content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"too many pixels" in response.data
    assert len(store.list_items()) == 6
    assert not store.upload_dir.exists()


def test_request_size_limit_returns_useful_error(tmp_path):
    client, store, _, report = setup(tmp_path)
    assert client.application.config["MAX_CONTENT_LENGTH"] == 25 * 1024 * 1024
    client.application.config["MAX_CONTENT_LENGTH"] = 512
    response = client.post("/items/new", data={**report, "photos": (
        BytesIO(b"x" * 1024), "too-large.jpg")}, content_type="multipart/form-data")
    assert response.status_code == 413
    assert b"total upload must be under 25 MB" in response.data
    assert len(store.list_items()) == 6


def test_version_two_migration_preserves_reports_and_claims(tmp_path):
    client, store, path, report = setup(tmp_path)
    client.post("/items/new", data=report)
    added = store.list_items({"q": "Black smartphone"})[0]
    claim = store.submit_claim(2, dict(name="Demo Claimant", contact="claimant@example.test",
                                       explanation="The case has a mark inside."))
    with closing(connect(path)) as connection:
        before_items = [tuple(row) for row in connection.execute("SELECT * FROM items ORDER BY id")]
        before_claims = [tuple(row) for row in connection.execute("SELECT * FROM claims ORDER BY id")]
        connection.execute("DROP TABLE item_photos")
        connection.execute("PRAGMA user_version = 2")
    initialize_database(path)
    initialize_database(path)
    with closing(connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 3
        assert [tuple(row) for row in connection.execute("SELECT * FROM items ORDER BY id")] == before_items
        assert [tuple(row) for row in connection.execute("SELECT * FROM claims ORDER BY id")] == before_claims
        assert connection.execute("SELECT COUNT(*) FROM item_photos").fetchone()[0] == 0
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("INSERT INTO item_photos(item_id,position,filename,width,height,byte_size) "
                               "VALUES (9999,1,'0123456789abcdef0123456789abcdef.webp',10,10,100)")
    assert SQLiteStore(path).get_item(added["id"])["title"] == "Black smartphone"
    assert SQLiteStore(path).list_claims()[0]["id"] == claim["id"]


def test_failed_photo_write_rolls_back_report_and_cleans_files(tmp_path):
    _, store, path, report = setup(tmp_path)
    report.pop("csrf_token")
    good = {"content": b"synthetic webp bytes", "width": 10, "height": 10}
    with pytest.raises(KeyError):
        store.create_item(report, [good, {"content": b"bad", "height": 10}])
    assert len(store.list_items()) == 6
    assert list(store.upload_dir.iterdir()) == []
    with closing(connect(path)) as connection:
        assert connection.execute("SELECT COUNT(*) FROM item_photos").fetchone()[0] == 0
