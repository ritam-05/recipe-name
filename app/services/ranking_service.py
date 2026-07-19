"""Recipe ranking based on emotion, intent, challenge, effort, ingredients, and nutrition."""

from __future__ import annotations

import re

from app.models.recipe import Recipe
from app.models.user_state import UserState


class RankingService:
    def rank(self, recipes: list[Recipe], user_state: UserState, limit: int = 3) -> list[Recipe]:
        scored_recipes = []
        for recipe in recipes:
            score, reasons = self._score_recipe(recipe, user_state)
            recipe.rank_score = round(score, 3)
            recipe.why_it_fits = reasons
            scored_recipes.append(recipe)

        scored_recipes.sort(key=lambda recipe: recipe.rank_score, reverse=True)
        return scored_recipes[:limit]

    def _score_recipe(self, recipe: Recipe, user_state: UserState) -> tuple[float, list[str]]:
        emotion_score, emotion_reason = self._emotion_score(recipe, user_state)
        challenge_score, challenge_reason = self._challenge_score(recipe, user_state)
        goal_score, goal_reason = self._goal_score(recipe, user_state)
        time_score, time_reason = self._time_score(recipe, user_state)
        ingredient_score, ingredient_reason = self._ingredient_score(recipe, user_state)
        nutrition_score, nutrition_reason = self._nutrition_score(recipe, user_state)
        cuisine_score, cuisine_reason = self._cuisine_score(recipe, user_state)

        final_score = (
            0.25 * emotion_score
            + 0.25 * challenge_score
            + 0.20 * goal_score
            + 0.10 * time_score
            + 0.10 * ingredient_score
            + 0.05 * nutrition_score
            + 0.05 * cuisine_score
        )

        reasons = [
            reason
            for reason in [
                emotion_reason,
                challenge_reason,
                goal_reason,
                time_reason,
                ingredient_reason,
                nutrition_reason,
                cuisine_reason,
            ]
            if reason
        ]
        return final_score, reasons[:4]

    def _emotion_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        emotion_set = {user_state.primary_emotion, user_state.secondary_emotion}
        if any(emotion and emotion in recipe.emotion_tags for emotion in emotion_set):
            return 1.0, "Matches your current mood."

        if user_state.preferred_tastes and any(
            taste.lower() in {profile.lower() for profile in recipe.taste_profile}
            for taste in user_state.preferred_tastes
        ):
            return 0.8, "Fits the taste style your mood seems to want."

        if user_state.comfort_food and recipe.comfort_score >= 7:
            return 0.75, "Leans into comfort in a way that fits your emotional state."

        if user_state.meal_type and recipe.meal_type == user_state.meal_type:
            return 0.65, f"Matches the meal type you seem to want: {user_state.meal_type}."

        return 0.35, "Still fits the request without fighting your mood."

    def _challenge_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        challenge_map = {"very_easy": 1, "easy": 2, "medium": 3, "hard": 4, "expert": 5}
        desired = challenge_map.get(user_state.challenge_level.lower(), 3)
        actual = max(1, min(5, recipe.difficulty_level))
        distance = abs(desired - actual)
        score = max(0.0, 1.0 - (distance / 4.0))

        if desired >= 4 and actual >= 4:
            reason = "Matches your request for a real challenge."
        elif desired <= 2 and actual <= 2:
            reason = "Stays easy and practical like you asked."
        elif distance == 0:
            reason = f"Fits your target difficulty level: {user_state.challenge_level}."
        else:
            reason = "Difficulty is close to what you seem to want."

        return score, reason

    def _goal_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        goal = user_state.goal.lower()
        goal_match = 0.0
        if goal == "learn":
            goal_match = min(1.0, (recipe.learning_value / 10.0) + (0.1 if recipe.difficulty_level >= 3 else 0.0))
            reason = "Supports your goal of learning and practicing real cooking skills."
        elif goal == "convenience":
            goal_match = 1.0 if recipe.difficulty_level <= 2 and recipe.total_minutes <= max(25, user_state.time_available or 25) else 0.45
            reason = "Keeps things simple and low-friction."
        elif goal == "explore":
            goal_match = 1.0 if len(recipe.skill_tags) >= 1 or recipe.difficulty_level >= 3 else 0.55
            reason = "Feels like a good recipe to explore and try something new."
        elif goal == "gourmet":
            goal_match = 1.0 if recipe.difficulty_level >= 4 else 0.5
            reason = "Feels restaurant-level or close to it."
        elif goal == "comfort":
            goal_match = min(1.0, recipe.comfort_score / 10.0)
            reason = "Leans into comfort and familiarity."
        else:
            goal_match = 0.7 if recipe.comfort_score >= 6 else 0.55
            reason = "Keeps the recipe balanced and practical."

        return goal_match, reason

    def _time_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        if not user_state.time_available:
            return 0.7, "Time is flexible, so the recipe length is acceptable."

        time_available = user_state.time_available
        recipe_time = recipe.total_minutes or self._parse_minutes(recipe.prep_time) + self._parse_minutes(recipe.cook_time)

        if user_state.goal in {"learn", "gourmet"}:
            if recipe_time <= time_available:
                score = 1.0
                reason = "Fits the time you said you have without rushing the process."
            else:
                score = max(0.6, 1.0 - ((recipe_time - time_available) / max(time_available, 60)))
                reason = "Longer cook time is acceptable because you want a more involved recipe."
            return score, reason

        if recipe_time <= time_available:
            score = 1.0
            reason = f"Fits inside your {time_available}-minute window."
        else:
            overflow = recipe_time - time_available
            score = max(0.0, 1.0 - (overflow / max(time_available, 20)))
            reason = "Runs a bit long, but still stays within a practical range."

        return score, reason

    def _ingredient_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        available = self._tokens(user_state.available_ingredients or user_state.ingredients)
        required = self._tokens(recipe.ingredients_needed)
        if not required:
            return 0.5, "Flexible ingredient list keeps it easy to adapt."

        overlap = len(available & required)
        score = min(1.0, overlap / max(1, min(len(required), 6)))

        if overlap >= 4:
            reason = "Uses a strong share of the ingredients you already have."
        elif overlap >= 2:
            reason = "Uses some of your ingredients and keeps shopping light."
        else:
            reason = "Can still work, but it may need more pantry items."

        return score, reason

    def _nutrition_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        base_score = max(0.0, min(1.0, recipe.nutrition_score / 10.0))
        if user_state.health_priority == "high":
            if recipe.nutrition_score >= 8.0:
                return base_score, "Keeps nutrition strong while staying aligned with your health goal."
            return base_score * 0.85, "Still reasonable, though not as nutrition-forward as the top options."

        if user_state.health_priority == "medium":
            return base_score * 0.95, "Balanced enough to stay practical and not too heavy."

        return base_score * 0.9 + 0.1, "Nutrition stays sensible without over-prioritizing it."

    def _cuisine_score(self, recipe: Recipe, user_state: UserState) -> tuple[float, str]:
        preferred = {taste.lower() for taste in user_state.preferred_tastes}
        cuisine = recipe.cuisine.lower()
        if any(term in cuisine for term in preferred):
            return 1.0, "Matches the flavor or cuisine direction you seem to prefer."
        if user_state.goal in {"learn", "gourmet", "explore"} and recipe.difficulty_level >= 3:
            return 0.75, "Uses a style that supports more ambitious cooking."
        return 0.6, "Cuisine keeps the recipe familiar enough to stay accessible."

    @staticmethod
    def _effort_level(value: str) -> float:
        normalized = value.strip().lower()
        mapping = {"minimal": 0.0, "low": 1.0, "medium": 2.0, "high": 3.0}
        return mapping.get(normalized, 1.5)

    @staticmethod
    def _parse_minutes(label: str) -> int:
        import re

        match = re.search(r"(\d+)", label or "")
        return int(match.group(1)) if match else 0

    @staticmethod
    def _budget_fit(recipe_budget: str, user_budget: str) -> float:
        recipe_value = {"low": 0.0, "medium": 0.5, "high": 1.0}.get(recipe_budget.strip().lower(), 0.5)
        user_value = {"low": 0.0, "medium": 0.5, "high": 1.0}.get(user_budget.strip().lower(), 0.5)
        return 1.0 - abs(recipe_value - user_value)

    @staticmethod
    def _spice_fit(recipe: Recipe, spice_level: str) -> float:
        spice_profile = {taste.lower() for taste in recipe.taste_profile}
        if spice_level == "hot":
            return 1.0 if "spicy" in spice_profile else 0.6
        if spice_level == "mild":
            return 1.0 if "spicy" not in spice_profile else 0.5
        return 0.8

    @staticmethod
    def _tokens(items: list[str]) -> set[str]:
        tokens: set[str] = set()
        for item in items:
            for token in re.findall(r"[a-z]+", item.lower()):
                tokens.add(token)
        return tokens
