"""Prompt helpers for structured recipe recommendation generation."""

from __future__ import annotations

import json
from dataclasses import asdict

from app.models.recipe import Recipe
from app.models.user_state import UserState


def build_recommendation_system_prompt() -> str:
    return """You are an emotionally aware recipe recommendation engine, not a generic chatbot.

Use the structured user state and the ranked candidate recipes you are given.
Do not invent new recipes. Do not reshuffle the ranking. Do not repeat the user's raw query.
Respond warmly and concisely.

Output JSON only with this shape:
{
  "intro": "short empathetic introduction",
  "why_selected": ["short reason 1", "short reason 2", "short reason 3"],
  "top_recommendation": "recipe name",
  "alternatives": ["recipe name", "recipe name"],
  "chef_tip": "one short chef tip",
  "nutrition_summary": "one concise nutrition sentence"
}

Style rules:
- Start with empathy.
- Keep it brief and practical.
- Explain the selection based on emotion, comfort, effort, time, ingredients, and nutrition.
- Never sound like a therapist.
- Never overwhelm the user.
"""


def build_recommendation_human_prompt(user_state: UserState, recipes: list[Recipe]) -> str:
    payload = {
        "user_state": asdict(user_state),
        "ranked_recipes": [
            {
                "name": recipe.name,
                "cuisine": recipe.cuisine,
                "difficulty": recipe.difficulty,
                "difficulty_level": recipe.difficulty_level,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_minutes": recipe.total_minutes,
                "comfort_score": recipe.comfort_score,
                "learning_value": recipe.learning_value,
                "techniques": recipe.techniques,
                "estimated_cleanup": recipe.estimated_cleanup,
                "skill_tags": recipe.skill_tags,
                "emotion_tags": recipe.emotion_tags,
                "taste_profile": recipe.taste_profile,
                "texture": recipe.texture,
                "temperature": recipe.temperature,
                "occasion": recipe.occasion,
                "energy_required": recipe.energy_required,
                "meal_type": recipe.meal_type,
                "budget": recipe.budget,
                "nutrition_score": recipe.nutrition_score,
                "rank_score": recipe.rank_score,
                "why_it_fits": recipe.why_it_fits,
                "ingredients_needed": recipe.ingredients_needed,
                "missing_ingredients": recipe.missing_ingredients,
                "nutrition_per_serving": recipe.nutrition_per_serving,
                "tips": recipe.tips,
            }
            for recipe in recipes
        ],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
