"""FindIt SDSU student project web application."""

from datetime import date, timedelta
import hmac
import os
import re
import secrets

from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.security import check_password_hash

from .matching import possible_matches
from .item_attributes import COLORS, ITEM_TYPES, ITEM_TYPE_CHOICES, ITEM_TYPE_CATEGORIES
from .photo_uploads import PhotoError, prepare_photos
from .storage import SQLiteStore
from .privacy import contains_contact


EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


def create_app(store=None):
    app = Flask(__name__)
    public = os.environ.get("FINDIT_PUBLIC") == "1"
    secret_key = os.environ.get("SECRET_KEY")
    password_hash = os.environ.get("PRESENTER_PASSWORD_HASH")
    if public and (not secret_key or not password_hash):
        raise RuntimeError("Public mode requires SECRET_KEY and PRESENTER_PASSWORD_HASH")
    app.secret_key = secret_key or secrets.token_hex(32)
    app.config.update(PRESENTER_AUTH_ENABLED=public or bool(password_hash),
                      PRESENTER_PASSWORD_HASH=password_hash,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                      SESSION_COOKIE_SECURE=public,
                      PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
    if public:
        hosts = [host.strip() for host in os.environ.get("FINDIT_ALLOWED_HOSTS", "finditsdsu.pythonanywhere.com").split(",") if host.strip()]
        app.config["TRUSTED_HOSTS"] = hosts
    app.config["STORE"] = store if store is not None else SQLiteStore()
    app.config["MAX_CONTENT_LENGTH"] = 18 * 1024 * 1024

    @app.errorhandler(413)
    def upload_too_large(_error):
        return render_template("report.html", values={},
                               errors={"photos": "The upload is too large. Choose up to three photos, 5 MB each."}), 413

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("error.html"), 500

    @app.template_filter("readable_date")
    def readable_date(value):
        reported = date.fromisoformat(value)
        return f"{reported:%b} {reported.day}, {reported.year}"

    @app.context_processor
    def shared_template_data():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)
        return {"categories": app.config["STORE"].list_categories(),
                "locations": app.config["STORE"].list_locations(),
                "item_type_choices": ITEM_TYPE_CHOICES,
                "item_type_categories": ITEM_TYPE_CATEGORIES, "colors": COLORS,
                "csrf_token": session["csrf_token"], "today": date.today().isoformat(),
                "presenter_auth_enabled": app.config["PRESENTER_AUTH_ENABLED"],
                "presenter_authenticated": bool(session.get("presenter"))}

    @app.before_request
    def verify_post_token():
        if (app.config["PRESENTER_AUTH_ENABLED"] and request.endpoint in
                {"new_item", "claim_item", "review_claims", "review_action"} and
                not session.get("presenter")):
            if request.method == "GET":
                return redirect(url_for("presenter_login", next=request.path))
            abort(403)
        token = session.get("csrf_token")
        if request.method == "POST" and (not token or not hmac.compare_digest(
            request.form.get("csrf_token", ""), token
        )):
            abort(400, "Please reload the form and try again.")

    @app.after_request
    def protect_private_responses(response):
        if request.endpoint in {"presenter_login", "presenter_logout", "claim_item",
                                "new_item", "review_claims", "review_action"}:
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.route("/presenter/login", methods=["GET", "POST"])
    def presenter_login():
        if not app.config["PRESENTER_AUTH_ENABLED"]:
            return redirect(url_for("home"))
        if session.get("presenter"):
            return redirect(url_for("home"))
        next_path = request.values.get("next", "")
        if not next_path.startswith("/") or next_path.startswith("//") or any(
                character in next_path for character in ("\\", "\r", "\n")):
            next_path = url_for("home")
        error = None
        if request.method == "POST":
            if check_password_hash(app.config["PRESENTER_PASSWORD_HASH"],
                                   request.form.get("password", "")):
                session.clear()
                session["presenter"] = True
                session.permanent = True
                flash("Signed in for the fictional classroom demonstration.", "success")
                return redirect(next_path)
            error = "That presenter password was not recognized."
        return render_template("login.html", error=error, next_path=next_path)

    @app.post("/presenter/logout")
    def presenter_logout():
        session.clear()
        flash("You have signed out.", "success")
        return redirect(url_for("home"))

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

    @app.get("/about")
    def about():
        return render_template("about.html")

    @app.get("/product")
    def product():
        return render_template("product.html")

    @app.get("/blog")
    def blog():
        return render_template("blog.html")

    @app.get("/resources")
    def resources():
        return render_template("resources.html")

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
        photos = []
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in
                      ("kind", "title", "description", "category", "location",
                       "report_date", "item_type", "brand", "model", "color", "contact_email")}
            if values["kind"] not in ("Lost", "Found"):
                errors["kind"] = "Choose lost or found."
            if not 4 <= len(values["title"]) <= 90:
                errors["title"] = "Enter a title between 4 and 90 characters."
            if not 12 <= len(values["description"]) <= 1200:
                errors["description"] = "Add at least 12 characters of detail (maximum 1,200)."
            elif contains_contact(values["description"]):
                errors["description"] = "Keep email addresses and phone numbers out of public details. Use the private contact field below."
            for field in ("title", "brand", "model"):
                if contains_contact(values[field]):
                    errors[field] = "Keep email addresses and phone numbers out of public details."
            if values["contact_email"] and (not 5 <= len(values["contact_email"]) <= 120 or
                                            not EMAIL.fullmatch(values["contact_email"])):
                errors["contact_email"] = "Enter a valid email address or leave this blank."
            if values["category"] not in store().list_categories():
                errors["category"] = "Choose a category."
            if values["item_type"] not in ITEM_TYPES.get(values["category"], ()):
                errors["item_type"] = "Choose an item type that fits the category."
            if len(values["brand"]) > 60:
                errors["brand"] = "Use 60 characters or fewer for the brand."
            if len(values["model"]) > 80:
                errors["model"] = "Use 80 characters or fewer for the model."
            if values["color"] and values["color"] not in COLORS:
                errors["color"] = "Choose a primary color from the list."
            if values["location"] not in store().list_locations():
                errors["location"] = "Choose a location."
            try:
                report_date = date.fromisoformat(values["report_date"])
                if values["report_date"] != report_date.isoformat() or report_date > date.today():
                    raise ValueError
            except ValueError:
                errors["report_date"] = "Choose a valid date that is not in the future."
            try:
                photos = prepare_photos(request.files.getlist("photos") +
                                        request.files.getlist("camera_photo"))
            except PhotoError as error:
                errors["photos"] = str(error)
            if not errors:
                try:
                    item = store().create_item(values, photos)
                except OSError:
                    app.logger.exception("Report photos could not be saved")
                    errors["photos"] = "Photos could not be saved. Please try again."
                    return render_template("report.html", values=values, errors=errors), 503
                flash("Your fictional report is live. Check the possible matches below as new reports arrive.", "success")
                return redirect(url_for("item_detail", item_id=item["id"]))
        return render_template("report.html", values=values, errors=errors)

    @app.get("/items/<int:item_id>")
    def item_detail(item_id):
        item = item_or_404(item_id)
        return render_template("detail.html", item=item, photos=store().list_photos(item_id),
                               matches=possible_matches(store(), item))

    @app.get("/photos/<int:photo_id>")
    def item_photo(photo_id):
        photo = store().get_photo(photo_id)
        if photo is None or not re.fullmatch(r"[0-9a-f]{32}\.webp", photo["file_name"]):
            abort(404)
        path = store().upload_dir / photo["file_name"]
        if not path.is_file():
            abort(404)
        response = send_file(path, mimetype="image/webp", conditional=True)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.route("/items/<int:item_id>/claim", methods=["GET", "POST"])
    def claim_item(item_id):
        item = item_or_404(item_id)
        if item["kind"] != "Found" or item["status"] != "Open":
            abort(404)
        values = {}
        errors = {}
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in ("name", "contact", "explanation")}
            if not 2 <= len(values["name"]) <= 80:
                errors["name"] = "Enter your name (2–80 characters)."
            if not 5 <= len(values["contact"]) <= 120 or not EMAIL.fullmatch(values["contact"]):
                errors["contact"] = "Enter a valid email address."
            if not 15 <= len(values["explanation"]) <= 1000:
                errors["explanation"] = "Add 15–1,000 characters to identify your item."
            if not errors:
                claim = store().submit_claim(item_id, values)
                if claim is None:
                    flash("This item can no longer be claimed.", "error")
                    return redirect(url_for("item_detail", item_id=item_id))
                if claim.get("error") == "duplicate":
                    errors["contact"] = "A claim using this email is already recorded for this item."
                    return render_template("claim.html", item=item, values=values, errors=errors), 409
                flash(f"Claim #{claim['id']} submitted. The presenter reviewer can now assess your private detail.", "success")
                return redirect(url_for("item_detail", item_id=item_id))
        return render_template("claim.html", item=item, values=values, errors=errors)

    @app.get("/review/claims")
    def review_claims():
        return render_template("review.html", claims=store().list_claims())

    @app.post("/review/claims/<int:claim_id>")
    def review_action(claim_id):
        action = request.form.get("action", "")
        if store().review_claim(claim_id, action):
            flash("Claim reviewed. The report has been updated.", "success")
        else:
            flash("This claim could not be reviewed. It may already be resolved.", "error")
        return redirect(url_for("review_claims"))

    return app
