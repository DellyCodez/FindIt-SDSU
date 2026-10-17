"""FindIt SDSU student project web application."""

from datetime import date
import hmac
import os
import re
import secrets

from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from .storage import SQLiteStore


def create_app(store=None):
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    app.config["STORE"] = store if store is not None else SQLiteStore()

    @app.context_processor
    def shared_template_data():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(24)
        return {"categories": app.config["STORE"].list_categories(),
                "locations": app.config["STORE"].list_locations(),
                "csrf_token": session["csrf_token"], "today": date.today().isoformat()}

    @app.before_request
    def verify_post_token():
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
        filters = {key: request.args.get(key, "").strip() for key in ("q", "kind", "category", "location")}
        if filters["kind"] not in ("", "Lost", "Found"):
            filters["kind"] = ""
        return render_template("items.html", items=store().list_items(filters), filters=filters)

    @app.route("/items/new", methods=["GET", "POST"])
    def new_item():
        values = {}
        errors = {}
        if request.method == "POST":
            values = {key: request.form.get(key, "").strip() for key in
                      ("kind", "title", "description", "category", "location", "report_date")}
            if values["kind"] not in ("Lost", "Found"):
                errors["kind"] = "Choose lost or found."
            if not 4 <= len(values["title"]) <= 90:
                errors["title"] = "Enter a title between 4 and 90 characters."
            if not 12 <= len(values["description"]) <= 1200:
                errors["description"] = "Add at least 12 characters of detail (maximum 1,200)."
            if values["category"] not in store().list_categories():
                errors["category"] = "Choose a category."
            if values["location"] not in store().list_locations():
                errors["location"] = "Choose a location."
            try:
                report_date = date.fromisoformat(values["report_date"])
                if report_date > date.today():
                    raise ValueError
            except ValueError:
                errors["report_date"] = "Choose a valid date that is not in the future."
            if not errors:
                item = store().create_item(values)
                flash("Your demo report is ready to view.", "success")
                return redirect(url_for("item_detail", item_id=item["id"]))
        return render_template("report.html", values=values, errors=errors)

    @app.get("/items/<int:item_id>")
    def item_detail(item_id):
        return render_template("detail.html", item=item_or_404(item_id))

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
            if not 5 <= len(values["contact"]) <= 120 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", values["contact"]):
                errors["contact"] = "Enter a valid email address."
            if not 15 <= len(values["explanation"]) <= 1000:
                errors["explanation"] = "Add 15–1,000 characters to identify your item."
            if not errors:
                claim = store().submit_claim(item_id, values)
                if claim is None:
                    flash("This item can no longer be claimed.", "error")
                    return redirect(url_for("item_detail", item_id=item_id))
                flash("Claim submitted for the local demo reviewer.", "success")
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
