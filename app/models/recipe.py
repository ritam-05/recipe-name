"""Recipe data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Recipe:
    name: str
    cuisine: str = "N/A"
    difficulty: str = "N/A"
    difficulty_level: int = 2
    prep_time: str = "N/A"
    cook_time: str = "N/A"
    servings: int | str = "N/A"
    comfort_score: int = 5
    learning_value: int = 0
    techniques: list[str] = field(default_factory=list)
    estimated_cleanup: str = "medium"
    skill_tags: list[str] = field(default_factory=list)
    emotion_tags: list[str] = field(default_factory=list)
    taste_profile: list[str] = field(default_factory=list)
    texture: str = ""
    temperature: str = ""
    occasion: str = ""
    energy_required: str = "medium"
    meal_type: str = "main"
    diet_tags: list[str] = field(default_factory=list)
    budget: str = "medium"
    prep_minutes: int = 0
    cook_minutes: int = 0
    total_minutes: int = 0
    nutrition_score: float = 5.0
    rank_score: float = 0.0
    why_it_fits: list[str] = field(default_factory=list)
    ingredients_needed: list[str] = field(default_factory=list)
    missing_ingredients: list[str] = field(default_factory=list)
    instructions: list[str] = field(default_factory=list)
    nutrition_per_serving: dict[str, Any] = field(default_factory=dict)
    tips: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Recipe":
        return cls(
            name=data.get("name", "Recipe"),
            cuisine=data.get("cuisine", "N/A"),
            difficulty=data.get("difficulty", "N/A"),
            difficulty_level=int(data.get("difficulty_level", 2)),
            prep_time=data.get("prep_time", "N/A"),
            cook_time=data.get("cook_time", "N/A"),
            servings=data.get("servings", "N/A"),
            comfort_score=int(data.get("comfort_score", 5)),
            learning_value=int(data.get("learning_value", 0)),
            techniques=list(data.get("techniques", [])),
            estimated_cleanup=data.get("estimated_cleanup", "medium"),
            skill_tags=list(data.get("skill_tags", [])),
            emotion_tags=list(data.get("emotion_tags", [])),
            taste_profile=list(data.get("taste_profile", [])),
            texture=data.get("texture", ""),
            temperature=data.get("temperature", ""),
            occasion=data.get("occasion", ""),
            energy_required=data.get("energy_required", "medium"),
            meal_type=data.get("meal_type", "main"),
            diet_tags=list(data.get("diet_tags", [])),
            budget=data.get("budget", "medium"),
            prep_minutes=int(data.get("prep_minutes", 0)),
            cook_minutes=int(data.get("cook_minutes", 0)),
            total_minutes=int(data.get("total_minutes", 0)),
            nutrition_score=float(data.get("nutrition_score", 5.0)),
            rank_score=float(data.get("rank_score", 0.0)),
            why_it_fits=list(data.get("why_it_fits", [])),
            ingredients_needed=list(data.get("ingredients_needed", [])),
            missing_ingredients=list(data.get("missing_ingredients", [])),
            instructions=list(data.get("instructions", [])),
            nutrition_per_serving=dict(data.get("nutrition_per_serving", {})),
            tips=data.get("tips", ""),
        )


@dataclass(slots=True)
class RecipeRecommendations:
    recipes: list[Recipe] = field(default_factory=list)
    recommended: str = "N/A"
    intro: str = ""
    top_recommendation: str = "N/A"
    alternatives: list[str] = field(default_factory=list)
    why_selected: list[str] = field(default_factory=list)
    chef_tip: str = ""
    nutrition_summary: str = ""
    matched_emotion: str = "neutral"
    secondary_emotion: str = ""
    confidence: float = 0.0
    matched_preferences: list[str] = field(default_factory=list)
    user_state: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RecipeRecommendations":
        recipes = [Recipe.from_dict(item) for item in data.get("recipes", [])]
        recommended = data.get("recommended") or (recipes[0].name if recipes else "N/A")
        return cls(
            recipes=recipes,
            recommended=recommended,
            intro=data.get("intro", ""),
            top_recommendation=data.get("top_recommendation", recommended),
            alternatives=list(data.get("alternatives", [])),
            why_selected=list(data.get("why_selected", [])),
            chef_tip=data.get("chef_tip", ""),
            nutrition_summary=data.get("nutrition_summary", ""),
            matched_emotion=data.get("matched_emotion", "neutral"),
            secondary_emotion=data.get("secondary_emotion", ""),
            confidence=float(data.get("confidence", 0.0)),
            matched_preferences=list(data.get("matched_preferences", [])),
            user_state=dict(data.get("user_state", {})),
        )
