"""General utility helpers."""

from __future__ import annotations

import re


def normalize_text(value: str) -> str:
    return value.strip().lower()


def extract_ingredients_from_request(request_text: str) -> list[str]:
    cleaned = request_text.strip()
    if not cleaned:
        return []

    lower_text = cleaned.lower()
    markers = (
        "i have these ingredients",
        "i have these ingredient",
        "i have",
        "i've got",
        "i got",
        "having",
        "with",
        "using",
        "containing",
        "ingredients",
        "ingredient",
    )

    candidate = cleaned
    for marker in markers:
        marker_index = lower_text.find(marker)
        if marker_index != -1:
            candidate = cleaned[marker_index + len(marker):]
            break

    candidate = re.split(
        r"\b(?:help me|please|cook something|make something|recommend something|for|time|in|under)\b",
        candidate,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    candidate = re.sub(r"^(?:these|this|the)?\s*ingredients?\b[:\s-]*", "", candidate, flags=re.IGNORECASE)
    candidate = re.sub(r"[?.!\"]+$", "", candidate)
    candidate = candidate.replace(" and ", ",")

    stop_words = {
        "help",
        "me",
        "cook",
        "something",
        "make",
        "recommend",
        "recipe",
        "recipes",
        "ingredients",
        "ingredient",
        "time",
        "hour",
        "hours",
        "minute",
        "minutes",
        "diet",
        "vegan",
        "vegetarian",
        "gluten-free",
        "keto",
        "and",
        "i",
        "have",
        "sad",
        "happy",
        "stressed",
        "anxious",
        "angry",
        "bored",
        "romantic",
        "tired",
        "sick",
        "nostalgic",
        "lonely",
        "celebratory",
        "adventurous",
        "focused",
        "lazy",
        "energetic",
        "guilty",
        "curious",
        "cozy",
        "heartbroken",
        "feeling",
        "feel",
        "feels",
        "exam",
        "tomorrow",
        "today",
        "tonight",
        "work",
        "workout",
        "breakup",
        "promotion",
    }

    parsed = []
    for part in candidate.split(","):
        item = part.strip(" ,.")
        if not item:
            continue
        if item.lower() in stop_words:
            continue
        if any(word in item.lower() for word in ("help", "cook", "time", "hour", "minute")):
            continue
        parsed.append(item)

    return parsed


def extract_time_limit_from_request(request_text: str) -> int:
    total_minutes = 0
    matches = re.findall(r"(\d+)\s*(hours?|hrs?|h|minutes?|mins?|m)\b", request_text.lower())
    for value, unit in matches:
        amount = int(value)
        if unit.startswith(("h", "hr")):
            total_minutes += amount * 60
        else:
            total_minutes += amount
    return total_minutes
