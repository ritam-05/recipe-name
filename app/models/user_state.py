"""Structured user state inferred from the request."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class UserState:
    query_text: str
    primary_emotion: str = "neutral"
    secondary_emotion: str = ""
    confidence: float = 0.0
    goal: str = "balance"
    challenge_level: str = "medium"
    effort_level: str = "medium"
    available_ingredients: list[str] = field(default_factory=list)
    comfort_food: bool = False
    energy_level: str = "medium"
    cooking_effort: str = "medium"
    time_available: int = 0
    health_priority: str = "low"
    budget: str = "medium"
    preferred_tastes: list[str] = field(default_factory=list)
    meal_type: str = "main"
    spice_level: str = "mild"
    ingredients: list[str] = field(default_factory=list)
    diet: str = ""
    servings: int = 2
    preference_inspirations: list[str] = field(default_factory=list)
