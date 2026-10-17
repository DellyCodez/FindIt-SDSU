"""Temporary, fictional, process-local data until the agreed SQLite schema arrives."""

from datetime import date, timedelta
from threading import RLock


CATEGORIES = ("Electronics", "Bags", "Drinkware", "Keys", "Clothing", "Other")
LOCATIONS = (
    "Library", "Student Union", "Engineering Building", "West Commons",
    "Arts and Letters", "Campus Green", "Other",
)


class DemoStore:
    def __init__(self):
        self._lock = RLock()
        today = date.today()
        examples = [
            ("Lost", "Red water bottle", "Matte red bottle with a black loop lid.", "Drinkware", "Library", 0, "bottle"),
            ("Found", "Black wireless earbuds", "Black earbuds in a matching charging case.", "Electronics", "Student Union", 1, "earbuds"),
            ("Lost", "Olive green backpack", "Canvas backpack with a small keychain on the zipper.", "Bags", "Engineering Building", 2, "backpack"),
            ("Found", "Silver key ring", "Three keys on a plain silver ring.", "Keys", "West Commons", 3, None),
            ("Lost", "Cream knit cardigan", "Lightweight cardigan with dark buttons.", "Clothing", "Arts and Letters", 4, None),
            ("Found", "Blue notebook", "Pocket notebook with a blue fabric cover.", "Other", "Campus Green", 5, None),
        ]
        self.items = [
            dict(id=i, kind=kind, title=title, description=description,
                 category=category, location=location,
                 report_date=(today - timedelta(days=days)).isoformat(),
                 status="Open", image=image, demo=True)
            for i, (kind, title, description, category, location, days, image)
            in enumerate(examples, 1)
        ]
        self.claims = []
        self._next_item_id = len(self.items) + 1
        self._next_claim_id = 1

    def list_items(self, filters=None):
        filters = filters or {}
        query = filters.get("q", "").strip().casefold()
        kind = filters.get("kind", "")
        category = filters.get("category", "")
        location = filters.get("location", "")
        with self._lock:
            items = [item.copy() for item in self.items if
                     (not query or query in " ".join((item["title"], item["description"], item["location"])).casefold())
                     and (not kind or item["kind"] == kind)
                     and (not category or item["category"] == category)
                     and (not location or item["location"] == location)]
        return sorted(items, key=lambda item: (item["report_date"], item["id"]), reverse=True)

    def get_item(self, item_id):
        with self._lock:
            return next((item.copy() for item in self.items if item["id"] == item_id), None)

    def create_item(self, data):
        with self._lock:
            item = dict(id=self._next_item_id, status="Open", image=None, demo=True, **data)
            self._next_item_id += 1
            self.items.append(item)
            return item.copy()

    def submit_claim(self, item_id, data):
        with self._lock:
            item = next((item for item in self.items if item["id"] == item_id), None)
            if not item or item["kind"] != "Found" or item["status"] != "Open":
                return None
            claim = dict(id=self._next_claim_id, item_id=item_id, status="Pending",
                         created_at=date.today().isoformat(), **data)
            self._next_claim_id += 1
            self.claims.append(claim)
            return claim.copy()

    def list_claims(self):
        with self._lock:
            return [dict(**claim, item=self.get_item(claim["item_id"]))
                    for claim in reversed(self.claims)]

    def review_claim(self, claim_id, action):
        with self._lock:
            claim = next((claim for claim in self.claims if claim["id"] == claim_id), None)
            if not claim or claim["status"] != "Pending" or action not in ("approve", "reject"):
                return False
            item = next((item for item in self.items if item["id"] == claim["item_id"]), None)
            if not item or item["kind"] != "Found":
                return False
            if action == "approve":
                if item["status"] != "Open" or any(
                    other["item_id"] == item["id"] and other["status"] == "Approved"
                    for other in self.claims
                ):
                    return False
                claim["status"] = "Approved"
                item["status"] = "Returned"
                for other in self.claims:
                    if other["item_id"] == item["id"] and other["status"] == "Pending":
                        other["status"] = "Rejected"
            else:
                claim["status"] = "Rejected"
            return True
