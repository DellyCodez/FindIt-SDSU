"""Basic public-text guard for contact details accidentally pasted into reports."""

import re


EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", re.I)
PHONE = re.compile(r"(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)")


def contains_contact(value):
    return bool(EMAIL.search(value) or PHONE.search(value))
