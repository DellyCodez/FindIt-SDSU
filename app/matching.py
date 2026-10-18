"""Deterministic suggestions using public report data only."""

from datetime import date
import re

from .item_types import recognized_type


STOP_WORDS = {
    "about", "after", "around", "campus", "case", "found", "from", "have",
    "item", "just", "large", "little", "lost", "near", "small", "some",
    "that", "their", "there", "this", "with", "the", "and", "for", "has",
    "was", "under", "inside", "outside", "black", "white", "blue",
    "brown", "cream", "gold", "gray", "green", "grey", "orange", "pink",
    "purple", "red", "silver", "yellow", "bottle", "water", "phone",
    "smartphone", "iphone", "earbud", "earbuds", "wireless", "laptop",
    "bag", "backpack", "key", "keys", "jacket", "notebook", "tote",
    "library", "building", "student", "union", "pro", "max",
}
COLORS = {"black", "blue", "brown", "cream", "gold", "gray", "green", "grey",
          "orange", "pink", "purple", "red", "silver", "white", "yellow"}


def words(value):
    terms = set()
    for word in re.findall(r"[a-z0-9]+", (value or "").lower()):
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("s") and not word.endswith("ss") and len(word) > 4:
            word = word[:-1]
        if len(word) >= 3 and word not in STOP_WORDS:
            terms.add(word)
    return terms


def color(item):
    explicit = (item.get("primary_color") or "").lower().strip()
    if explicit:
        named = set(re.findall(r"[a-z]+", explicit)) & COLORS
        return {"grey" if value == "gray" else value for value in named} or {explicit}
    found = set(re.findall(r"[a-z]+", (item["title"] + " " + item["description"]).lower())) & COLORS
    return {"grey" if value == "gray" else value for value in found}


def normalized(value):
    return " ".join(re.findall(r"[a-z0-9]+", (value or "").lower()))


def same_model(first, second):
    if not first or not second:
        return False
    family_words = {"iphone", "ipad", "macbook", "galaxy", "pixel", "phone", "laptop", "tablet"}
    first_words, second_words = set(first.split()), set(second.split())
    first_family, second_family = first_words & family_words, second_words & family_words
    if first_family and second_family and first_family != second_family:
        return False
    left = first_words - family_words
    right = second_words - family_words
    return bool(left) and left == right


def possible_matches(store, item, limit=3):
    """Return ranked leads; scores describe heuristic similarity, not ownership odds."""
    if item["status"] != "Open":
        return []
    when = date.fromisoformat(item["report_date"])
    ordinal = when.toordinal()
    first_offset, last_offset = (-2, 45) if item["kind"] == "Lost" else (-45, 2)
    first = date.fromordinal(max(1, ordinal + first_offset)).isoformat()
    last = date.fromordinal(min(date.max.toordinal(), ordinal + last_offset)).isoformat()
    source_type = recognized_type(item)
    source_colors = color(item)
    source_words = words(" ".join((item["title"], item["description"],
                                   item.get("distinguishing_features") or "")))
    results = []
    for other in store.match_candidates(item, first, last):
        other_type = recognized_type(other)
        if source_type and other_type and source_type != other_type:
            continue
        other_colors = color(other)
        if source_colors and other_colors and not source_colors & other_colors:
            continue
        brand = normalized(item.get("brand"))
        other_brand = normalized(other.get("brand"))
        model = normalized(item.get("model"))
        other_model = normalized(other.get("model"))
        if brand and other_brand and brand != other_brand:
            continue
        if model and other_model and not same_model(model, other_model):
            continue
        shared = source_words & words(" ".join((other["title"], other["description"],
                                                other.get("distinguishing_features") or "")))
        matching_model = same_model(model, other_model)
        matching_color = bool(source_colors and other_colors and source_colors & other_colors)
        # Place/date and generic words never form a lead on their own.
        if not shared and not matching_model:
            continue
        if not source_type or not other_type:
            if len(shared) < 2 and not matching_model:
                continue
        if item["category"] == "Other" and len(shared) < 2 and not matching_model:
            continue
        days = abs((when - date.fromisoformat(other["report_date"])).days)
        score = 20 + (34 if source_type and other_type else 6 if source_type or other_type else 0)
        score += min(24, len(shared) * 8)
        score += 8 if matching_color else 0
        score += 10 if brand and other_brand and brand == other_brand else 0
        score += 16 if matching_model else 0
        score += 6 if item["location_id"] == other["location_id"] else 0
        score += 7 if days <= 2 else 4 if days <= 7 else 2 if days <= 14 else 0
        if score < 58:
            continue
        reasons = ["Same category"]
        if source_type and other_type:
            reasons.append(f"Both appear to be {source_type.lower()} reports")
        if matching_model:
            reasons.append("Same model")
        elif brand and other_brand and brand == other_brand:
            reasons.append("Same brand")
        if matching_color:
            reasons.append("Matching color")
        if item["location_id"] == other["location_id"]:
            reasons.append("Same location")
        if days <= 14:
            reasons.append("Dates close together")
        if shared:
            reasons.append("Shared details: " + ", ".join(sorted(shared)[:3]))
        results.append({"item": other, "score": min(score, 100), "reasons": reasons})
    return sorted(results, key=lambda match: (-match["score"], -match["item"]["id"]))[:limit]
