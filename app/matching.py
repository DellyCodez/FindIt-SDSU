"""Deterministic suggestions using only public lost and found report fields."""

from datetime import date
import re

from .item_attributes import COLORS, resolved_type


COLOR_WORDS = {color.lower() for color in COLORS if color != "Other"}
GENERIC_WORDS = {
    "about", "after", "around", "campus", "case", "cover", "found",
    "from", "have", "item", "just", "large", "little", "lost", "near",
    "small", "some", "that", "their", "there", "this", "with", "the",
    "phone", "smartphone", "iphone", "earbud", "airpod", "laptop", "backpack",
    "bottle", "water", "key", "keys", "wallet", "notebook", "jacket", "bag",
    "and", "for", "was", "under", "inside", "outside", "wireless", "pro", "max",
    "fictional", "demo",
}
GENERIC_WORDS |= COLOR_WORDS


def words(value):
    terms = set()
    for word in re.findall(r"[a-z0-9]+", value.lower()):
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("s") and not word.endswith("ss") and len(word) > 4:
            word = word[:-1]
        if len(word) >= 3 and len(word) <= 24 and word not in GENERIC_WORDS and not (word.isdigit() and len(word) > 6):
            terms.add(word)
    return terms


def primary_color(item):
    if item.get("color") and item["color"] != "Other":
        return item["color"].lower()
    for field in ("title", "description"):
        for word in re.findall(r"[a-z]+", item[field].lower()):
            if word in COLOR_WORDS:
                return "gray" if word == "grey" else word
    return None


def same_attribute(first, second, key):
    left, right = first.get(key), second.get(key)
    if key == "model":
        return same_model(left, right)
    return bool(left and right and left.casefold().strip() == right.casefold().strip())


def same_model(first, second):
    """Allow an omitted device family, but never equate conflicting families."""
    left = set(re.findall(r"[a-z0-9]+", (first or "").lower()))
    right = set(re.findall(r"[a-z0-9]+", (second or "").lower()))
    if not left or not right:
        return False
    families = {"iphone", "ipad", "macbook", "galaxy", "pixel", "phone", "laptop", "tablet"}
    left_family, right_family = left & families, right & families
    if left_family and right_family and left_family != right_family:
        return False
    return bool(left - families) and left - families == right - families


def possible_matches(store, item, limit=3):
    """Rank plausible opposite-type reports; a score is similarity, not ownership proof."""
    if item["status"] != "Open":
        return []
    when = date.fromisoformat(item["report_date"])
    ordinal = when.toordinal()
    first_offset, last_offset = (-2, 45) if item["kind"] == "Lost" else (-45, 2)
    first = date.fromordinal(max(1, ordinal + first_offset)).isoformat()
    last = date.fromordinal(min(date.max.toordinal(), ordinal + last_offset)).isoformat()
    item_type = resolved_type(item)
    source_title = words(item["title"])
    source_words = words(item["title"] + " " + item["description"] + " " +
                         (item.get("distinguishing_features") or ""))
    source_color = primary_color(item)
    results = []
    for other in store.match_candidates(item, first, last):
        other_type = resolved_type(other)
        if item_type and other_type and item_type != other_type:
            continue
        if item.get("brand") and other.get("brand") and not same_attribute(item, other, "brand"):
            continue
        if item.get("model") and other.get("model") and not same_attribute(item, other, "model"):
            continue
        other_color = primary_color(other)
        if source_color and other_color and source_color != other_color:
            continue
        title_shared = source_title & words(other["title"])
        shared = source_words & words(other["title"] + " " + other["description"] + " " +
                                      (other.get("distinguishing_features") or ""))
        brand_match = same_attribute(item, other, "brand")
        model_match = same_attribute(item, other, "model")
        if not shared and not (brand_match and model_match):
            continue
        if (not item_type or not other_type or item["category"] == "Other") and len(shared) < 2 and not model_match:
            continue
        days = abs((when - date.fromisoformat(other["report_date"])).days)
        date_points = 10 if days <= 2 else 8 if days <= 7 else 5 if days <= 14 else 2
        detail_points = min(20, 10 * len(title_shared) + 4 * len(shared - title_shared))
        score = 20 + (22 if item_type and item_type == other_type else 0)
        score += (12 if item["location_id"] == other["location_id"] else 0) + date_points
        score += detail_points + (6 if brand_match else 0) + (10 if model_match else 0)
        score += 5 if source_color and source_color == other_color else 0
        if score < 55:
            continue
        reasons = ["Same category"]
        if item_type and item_type == other_type:
            reasons.append("Same item type: " + item_type)
        if item["location_id"] == other["location_id"]:
            reasons.append("Same location")
        if days <= 14:
            reasons.append("Dates close together")
        if brand_match:
            reasons.append("Matching brand: " + item["brand"])
        if model_match:
            reasons.append("Matching model: " + item["model"])
        if source_color and source_color == other_color:
            reasons.append("Matching color: " + source_color.title())
        if shared:
            prominent = sorted(title_shared) + sorted(shared - title_shared)
            reasons.append("Shared details: " + ", ".join(prominent[:3]))
        results.append({"item": other, "score": min(100, score), "reasons": reasons})
    return sorted(results, key=lambda match: (-match["score"], -match["item"]["id"]))[:limit]
