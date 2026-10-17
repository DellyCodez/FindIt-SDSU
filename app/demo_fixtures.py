"""Small fictional starter set for a fresh local SQLite database."""

from datetime import date, timedelta


CATEGORIES = ("Electronics", "Bags", "Drinkware", "Keys", "Clothing", "Other")
LOCATIONS = (
    "Library", "Student Union", "Engineering Building", "West Commons",
    "Arts and Letters", "Campus Green", "Other",
)


def demo_items():
    today = date.today()
    examples = [
        ("Lost", "Red water bottle", "Matte red bottle with a black loop lid.", "Drinkware", "Library", 0, "bottle"),
        ("Found", "Black wireless earbuds", "Black earbuds in a matching charging case.", "Electronics", "Student Union", 1, "earbuds"),
        ("Lost", "Olive green backpack", "Canvas backpack with a small keychain on the zipper.", "Bags", "Engineering Building", 2, "backpack"),
        ("Found", "Silver key ring", "Three keys on a plain silver ring.", "Keys", "West Commons", 3, None),
        ("Lost", "Cream knit cardigan", "Lightweight cardigan with dark buttons.", "Clothing", "Arts and Letters", 4, None),
        ("Found", "Blue notebook", "Pocket notebook with a blue fabric cover.", "Other", "Campus Green", 5, None),
    ]
    return [
        dict(kind=kind, title=title, description=description,
             category=category, location=location,
             report_date=(today - timedelta(days=days)).isoformat(), image=image)
        for kind, title, description, category, location, days, image in examples
    ]
