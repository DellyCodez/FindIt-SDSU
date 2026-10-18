"""Shared report choices and conservative legacy type recognition."""

import re


ITEM_TYPES = {
    "Electronics": ("Smartphone", "Earbuds", "Headphones", "Laptop", "Tablet", "Camera", "Other"),
    "Drinkware": ("Water Bottle", "Tumbler", "Thermos", "Mug", "Other"),
    "Bags": ("Backpack", "Tote Bag", "Handbag", "Satchel", "Other"),
    "Clothing": ("Jacket", "Hoodie", "Sweater", "Cardigan", "Shirt", "Other"),
    "Accessories": ("Wallet", "Keys", "Sunglasses", "Watch", "Other"),
    "Keys": ("Keys", "Other"),
    "Other": ("Notebook", "Umbrella", "Other"),
}

ALIASES = {
    "Smartphone": r"\b(?:smartphone|i(?:phone|pad phone)|pixel phone|galaxy phone|phone)\b",
    "Earbuds": r"\b(?:earbuds?|airpods?|earphones?)\b",
    "Headphones": r"\bheadphones?\b",
    "Laptop": r"\b(?:laptop|macbook|notebook computer)\b",
    "Tablet": r"\b(?:tablet|ipad)\b",
    "Camera": r"\bcamera\b",
    "Water Bottle": r"\b(?:water bottle|bottle)\b",
    "Tumbler": r"\btumbler\b",
    "Thermos": r"\b(?:thermos|flask)\b",
    "Mug": r"\bmug\b",
    "Backpack": r"\bbackpack\b",
    "Tote Bag": r"\btote(?: bag)?\b",
    "Handbag": r"\bhandbag\b",
    "Satchel": r"\bsatchel\b",
    "Jacket": r"\bjacket\b",
    "Hoodie": r"\bhoodie\b",
    "Sweater": r"\bsweater\b",
    "Cardigan": r"\bcardigan\b",
    "Shirt": r"\bshirt\b",
    "Wallet": r"\bwallet\b",
    "Keys": r"\bkeys?\b",
    "Sunglasses": r"\bsunglasses?\b",
    "Watch": r"\bwatch\b",
    "Notebook": r"\bnotebook\b",
    "Umbrella": r"\bumbrella\b",
}


def recognized_type(item):
    """Read explicit type, or cautiously infer from a legacy public title only."""
    explicit = item.get("item_type")
    if explicit and explicit != "Other":
        return explicit
    title = item.get("title", "").lower()
    candidates = [name for name in ITEM_TYPES.get(item["category"], ())
                  if name in ALIASES and re.search(ALIASES[name], title)]
    return candidates[0] if len(candidates) == 1 else None
