"""Parsed recipe request data."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RecipeRequest:
    query_text: str
    ingredients: list[str] = field(default_factory=list)
    diet: str = ""
    time_limit: int = 0
    servings: int = 2
