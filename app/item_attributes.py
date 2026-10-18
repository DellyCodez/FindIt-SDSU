"""Small controlled vocabulary for new reports and legacy type inference."""

import re


ITEM_TYPES = {
    "Electronics": ("Smartphone", "Earbuds", "Laptop", "Other"),
    "Bags": ("Backpack", "Wallet", "Other"),
    "Drinkware": ("Water Bottle", "Other"),
    "Keys": ("Keys", "Other"),
    "Clothing": ("Clothing", "Other"),
    "Accessories": ("Wallet", "Keys", "Other"),
    "Other": ("Notebook", "Other"),
}
ITEM_TYPE_CHOICES = tuple(dict.fromkeys(
    item_type for choices in ITEM_TYPES.values() for item_type in choices))
ITEM_TYPE_CATEGORIES = {
    item_type: tuple(category for category, choices in ITEM_TYPES.items()
                     if item_type in choices)
    for item_type in ITEM_TYPE_CHOICES
}
COLORS = ("Black", "Blue", "Brown", "Cream", "Gold", "Gray", "Green",
          "Orange", "Pink", "Purple", "Red", "Silver", "White", "Yellow", "Other")

LEGACY_TYPES = (
    ("Smartphone", r"\b(?:iphone|pixel|galaxy|smartphone|phone)\b"),
    ("Earbuds", r"\b(?:airpods?|earbuds?|earphones?)\b"),
    ("Laptop", r"\b(?:laptop|macbook|thinkpad)\b"),
    ("Backpack", r"\b(?:backpacks?|rucksacks?)\b"),
    ("Water Bottle", r"\b(?:bottles?|thermos|flasks?)\b"),
    ("Keys", r"\b(?:keys?|keyring|keychain)\b"),
    ("Wallet", r"\b(?:wallets?|purses?)\b"),
    ("Notebook", r"\b(?:notebooks?|journals?)\b"),
    ("Clothing", r"\b(?:jackets?|cardigans?|hoodies?|sweaters?|shirts?)\b"),
)


def resolved_type(item):
    if item.get("item_type") and item["item_type"] != "Other":
        return item["item_type"]
    title = item["title"].lower()
    for item_type, pattern in LEGACY_TYPES:
        if re.search(pattern, title):
            return item_type
    return None
