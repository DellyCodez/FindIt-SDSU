"""FindIt SDSU student project web application."""

from datetime import date
import hmac
import os
import re
import secrets

from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from .matching import possible_matches
from .item_types import ITEM_TYPES
from .photos import PhotoValidationError, prepare_photos
from .privacy import contains_contact
from .storage import SQLiteStore


def create_app(store=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["STORE"] = store if store is not None else SQLiteStore()
    app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024

    @app.errorhandler(RequestEntityTooLarge)
    def too_large(error):
        return render_template("report.html", values={},
                               errors={"photos": "The total upload must be under 25 MB. Choose smaller photos."}), 413

    @app.template_filter("readable_date")
    def readable_date(value):
        reported = date.fromisoformat(value)
        return f"{reported:%b} {reported.day}, {reported.year}"

    @app.template_filter("illustration_type")
    def illustration_type(item):
        if item.get("item_type") == "Smartphone":
            return "phone"
        if item.get("item_type") == "Earbuds":
            return "earbuds"
        if item.get("item_type") == "Laptop":
            return "laptop"
        if item["category"] != "Electronics":
            return item["category"].lower()
        title = item["title"].lower()
        if re.search(r"\b(phone|smartphone|iphone|pixel|galaxy)\b", title):
            return "phone"
        if re.search(r"\b(earbuds?|airpods?|headphones?)\b", title):
            return "earbuds"
        if re.search(r"\b(laptop|macbook|notebook computer)\b", title):
            return "laptop"
        return "electronics"

    @app.context_processor
    def shared_template_data():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)
        return {"categories": app.config["STORE"].list_categories(),
                "locations": app.config["STORE"].list_locations(),
                "csrf_token": session["csrf_token"], "today": date.today().isoformat(),
                "item_types": ITEM_TYPES}

    @app.before_request
    def verify_post_token():
        if request.path.startswith("/review/") and request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)
        token = session.get("csrf_token")
        if request.method == "POST" and (not token or not hmac.compare_digest(
            request.form.get("csrf_token", ""), token
        )):
            abort(400, "Please reload the form and try again.")

    def store():
        return app.config["STORE"]

    def item_or_404(item_id):
        item = store().get_item(item_id)
        if item is None:
            abort(404)
        return item

    @app.get("/")
    def home():
        return render_template("home.html", items=store().list_items()[:3])

    @app.get("/items")
    def items():
        filters = {key: request.args.get(key, "").strip() for key in ("q", "kind", "category", "location", "sort")}
        if filters["kind"] not in ("", "Lost", "Found"):
            filters["kind"] = ""
        if filters["sort"] not in ("newest", "oldest", "relevance") or (
            filters["sort"] == "relevance" and not filters["q"]
        ):
            filters["sort"] = "relevance" if filters["q"] else "newest"
        return render_template("items.html", items=store().list_items(filters),
                               filters=filters, show_sort=True)

    @app.route("/items/new", methods=["GET", "POST"])
    def new_item():
        values = {}
        errors = {}
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in
                      ("kind", "title", "description", "category", "location", "report_date",
                       "item_type", "brand", "model", "primary_color", "distinguishing_features")}
            if values["kind"] not in ("Lost", "Found"):
                errors["kind"] = "Choose lost or found."
            if not 4 <= len(values["title"]) <= 90:
                errors["title"] = "Enter a title between 4 and 90 characters."
            if not 12 <= len(values["description"]) <= 1200:
                errors["description"] = "Add at least 12 characters of detail (maximum 1,200)."
            if values["category"] not in store().list_categories():
                errors["category"] = "Choose a category."
            if values["category"] in ITEM_TYPES and values["item_type"] not in ITEM_TYPES[values["category"]]:
                errors["item_type"] = "Choose an item type for this category."
            for field, maximum in (("brand", 60), ("model", 60),
                                   ("distinguishing_features", 300)):
                if values[field] and not (3 if field == "distinguishing_features" else 1) <= len(values[field]) <= maximum:
                    errors[field] = f"Use no more than {maximum} characters."
            if not 2 <= len(values["primary_color"]) <= 40:
                errors["primary_color"] = "Enter the item's primary color (2–40 characters)."
            for field in ("title", "description", "brand", "model", "primary_color", "distinguishing_features"):
                if contains_contact(values[field]):
                    errors[field] = "Remove email addresses and phone numbers from this public field. Use the private claim form for contact details."
            if values["location"] not in store().list_locations():
                errors["location"] = "Choose a location."
            try:
                report_date = date.fromisoformat(values["report_date"])
                if values["report_date"] != report_date.isoformat() or report_date > date.today():
                    raise ValueError
            except ValueError:
                errors["report_date"] = "Choose a valid date that is not in the future."
            try:
                photos = prepare_photos(request.files.getlist("photos"))
            except PhotoValidationError as error:
                errors["photos"] = str(error)
            if not errors:
                try:
                    item = store().create_item(values, photos)
                except OSError:
                    errors["photos"] = "Photos could not be saved. Please try again."
                    return render_template("report.html", values=values, errors=errors), 503
                flash("Your fictional report is live. Check the possible matches below as new reports arrive.", "success")
                return redirect(url_for("item_detail", item_id=item["id"]))
        return render_template("report.html", values=values, errors=errors)

    @app.get("/items/<int:item_id>")
    def item_detail(item_id):
        item = item_or_404(item_id)
        return render_template("detail.html", item=item, photos=store().get_photos(item_id),
                               matches=possible_matches(store(), item))

    @app.get("/items/<int:item_id>/photos/<int:photo_id>")
    def item_photo(item_id, photo_id):
        path = store().photo_path(item_id, photo_id)
        if path is None or not path.is_file():
            abort(404)
        response = send_file(path, mimetype="image/webp", max_age=3600)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.route("/items/<int:item_id>/claim", methods=["GET", "POST"])
    def claim_item(item_id):
        item = item_or_404(item_id)
        if item["kind"] != "Found":
            abort(404)
        if item["status"] != "Open":
            flash("This item has already been returned and no longer accepts claims.", "error")
            return redirect(url_for("item_detail", item_id=item_id))
        values = {}
        errors = {}
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in ("name", "contact", "explanation")}
            if not 2 <= len(values["name"]) <= 80:
                errors["name"] = "Enter your name (2–80 characters)."
            if not 5 <= len(values["contact"]) <= 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", values["contact"]):
                errors["contact"] = "Enter a valid email address."
            if not 15 <= len(values["explanation"]) <= 1000:
                errors["explanation"] = "Add 15–1,000 characters to identify your item."
            if not errors:
                claim = store().submit_claim(item_id, values)
                if claim is None:
                    flash("This item can no longer be claimed.", "error")
                    return redirect(url_for("item_detail", item_id=item_id))
                if claim.get("error") == "duplicate":
                    errors["contact"] = "A claim using this email is already recorded for this item. Ask the local demo reviewer about its status."
                    return render_template("claim.html", item=item, values=values, errors=errors), 409
                flash("Claim submitted. Its identifying detail is visible only to the local demo reviewer. Review is pending; a suggestion score does not verify ownership.", "success")
                return redirect(url_for("item_detail", item_id=item_id))
        return render_template("claim.html", item=item, values=values, errors=errors)

    @app.get("/review/claims")
    def review_claims():
        return render_template("review.html", claims=store().list_claims())

    @app.post("/review/claims/<int:claim_id>")
    def review_action(claim_id):
        action = request.form.get("action", "")
        if store().review_claim(claim_id, action):
            flash("Claim approved and item returned." if action == "approve" else "Claim rejected. The item remains open.", "success")
        else:
            flash("This claim could not be reviewed. It may already be resolved.", "error")
        return redirect(url_for("review_claims"))

    return app
