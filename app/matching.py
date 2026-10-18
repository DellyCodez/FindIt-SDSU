"""Explainable suggestions based only on public lost and found report fields."""

from datetime import date
import re


COMMON_WORDS = {
    "about", "after", "around", "campus", "found", "from", "have",
    "item", "just", "large", "little", "lost", "near", "small", "some",
    "that", "their", "there", "this", "with",
}
COLORS = {"black", "blue", "brown", "cream", "gold", "gray", "green", "grey",
          "orange", "pink", "purple", "red", "silver", "white", "yellow"}


def words(value):
    terms = set()
    for word in re.findall(r"[a-z0-9]+", value.lower()):
        if word.endswith("ies") and len(word) > 5:
            word = word[:-3] + "y"
        elif word.endswith("s") and not word.endswith("ss") and len(word) > 4:
            word = word[:-1]
        if len(word) >= 3 and word not in COMMON_WORDS:
            terms.add(word)
    return terms


def possible_matches(store, item, limit=3):
    """Rank same-category, open, opposite-type reports within a plausible date window.

    This heuristic suggests reports for human review; it never confirms ownership.
    """
    if item["status"] != "Open":
        return []
    when = date.fromisoformat(item["report_date"])
    # Clamp at the representable date boundaries before constructing date objects.
    ordinal = when.toordinal()
    if item["kind"] == "Lost":
        first_offset, last_offset = -2, 45
    else:
        first_offset, last_offset = -45, 2
    first = date.fromordinal(max(1, ordinal + first_offset)).isoformat()
    last = date.fromordinal(min(date.max.toordinal(), ordinal + last_offset)).isoformat()
    source_title = words(item["title"])
    source_words = words(item["title"] + " " + item["description"])
    source_colors = set(re.findall(r"[a-z]+", (item["title"] + " " + item["description"]).lower())) & COLORS
    results = []
    for other in store.match_candidates(item, first, last):
        other_title = words(other["title"])
        other_words = words(other["title"] + " " + other["description"])
        shared = source_words & other_words
        other_colors = set(re.findall(r"[a-z]+", (other["title"] + " " + other["description"]).lower())) & COLORS
        # Color by itself is too weak to connect two items in a broad category.
        if not (shared - COLORS) or (source_colors and other_colors and not source_colors & other_colors):
            continue
        if item["category"] == "Other" and len(shared) < 2:
            continue
        title_shared = source_title & other_title
        days = abs((when - date.fromisoformat(other["report_date"])).days)
        date_points = 15 if days <= 2 else 10 if days <= 7 else 6 if days <= 14 else 2
        word_points = min(30, 12 * len(title_shared) + 5 * len(shared - title_shared))
        score = 35 + (18 if item["location_id"] == other["location_id"] else 0) + date_points + word_points
        if score < 60:
            continue
        reasons = ["Same category"]
        if item["location_id"] == other["location_id"]:
            reasons.append("Same location")
        if days <= 14:
            reasons.append("Dates close together")
        prominent_words = sorted(title_shared) + sorted(shared - title_shared)
        reasons.append("Shared words: " + ", ".join(prominent_words[:3]))
        results.append({"item": other, "score": score, "reasons": reasons})
    return sorted(results, key=lambda match: (-match["score"], -match["item"]["id"]))[:limit]
