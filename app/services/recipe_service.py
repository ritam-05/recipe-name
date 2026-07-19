"""Recipe generation service."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.models.recipe import RecipeRecommendations
from app.parsers.json_parser import parse_json_response
from app.prompts.recipe_prompt import build_recommendation_human_prompt, build_recommendation_system_prompt
from app.services.intent_service import IntentService
from app.services.llm_service import LLMService
from app.services.ranking_service import RankingService
from app.services.retrieval_service import RetrievalService


class RecipeService:
    def __init__(self) -> None:
        self.intent_service = IntentService()
        self.retrieval_service = RetrievalService()
        self.ranking_service = RankingService()
        self.llm_service = LLMService()

    def get_recipes(
        self,
        query_text: str,
        diet: str = "",
        time_limit: int = 0,
        servings: int = 2,
    ) -> RecipeRecommendations:
        user_state = self.intent_service.build_user_state(query_text, diet, time_limit, servings)
        retrieved_recipes = self.retrieval_service.retrieve(user_state)
        ranked_recipes = self.ranking_service.rank(retrieved_recipes, user_state)

        recommendations = self._build_fallback_response(user_state, ranked_recipes)

        try:
            messages = [
                SystemMessage(content=build_recommendation_system_prompt()),
                HumanMessage(content=build_recommendation_human_prompt(user_state, ranked_recipes)),
            ]
            response = self.llm_service.invoke(messages)
            parsed = parse_json_response(response.content)
            recommendations = self._merge_llm_response(recommendations, parsed)
        except Exception:
            pass

        return recommendations

    def _build_fallback_response(self, user_state, ranked_recipes) -> RecipeRecommendations:
        if ranked_recipes:
            top_recipe = ranked_recipes[0]
            alternatives = [recipe.name for recipe in ranked_recipes[1:]]
            intro = self._build_intro(user_state)
            why_selected = [f"{recipe.name}: {recipe.why_it_fits[0]}" for recipe in ranked_recipes if recipe.why_it_fits]
            nutrition_summary = self._build_nutrition_summary(top_recipe)
            chef_tip = top_recipe.tips
            recommended = top_recipe.name
        else:
            top_recipe = None
            alternatives = []
            intro = self._build_intro(user_state)
            why_selected = ["I couldn't find a strong match, so I stayed conservative with the fallback options."]
            nutrition_summary = ""
            chef_tip = ""
            recommended = "N/A"

        return RecipeRecommendations(
            recipes=ranked_recipes,
            recommended=recommended,
            intro=intro,
            top_recommendation=recommended,
            alternatives=alternatives,
            why_selected=why_selected,
            chef_tip=chef_tip,
            nutrition_summary=nutrition_summary,
            matched_emotion=user_state.primary_emotion,
            secondary_emotion=user_state.secondary_emotion,
            confidence=user_state.confidence,
            matched_preferences=user_state.preference_inspirations,
            user_state={
                "primary_emotion": user_state.primary_emotion,
                "secondary_emotion": user_state.secondary_emotion,
                "goal": user_state.goal,
                "challenge_level": user_state.challenge_level,
                "effort_level": user_state.effort_level,
                "comfort_food": user_state.comfort_food,
                "energy_level": user_state.energy_level,
                "cooking_effort": user_state.cooking_effort,
                "time_available": user_state.time_available,
                "health_priority": user_state.health_priority,
                "budget": user_state.budget,
                "preferred_tastes": user_state.preferred_tastes,
                "meal_type": user_state.meal_type,
                "spice_level": user_state.spice_level,
                "ingredients": user_state.ingredients,
                "available_ingredients": user_state.available_ingredients,
                "confidence": user_state.confidence,
            },
        )

    def _merge_llm_response(self, fallback: RecipeRecommendations, parsed: dict) -> RecipeRecommendations:
        fallback.intro = parsed.get("intro", fallback.intro)
        fallback.why_selected = list(parsed.get("why_selected", fallback.why_selected))
        fallback.top_recommendation = parsed.get("top_recommendation", fallback.top_recommendation)
        fallback.recommended = fallback.top_recommendation
        fallback.alternatives = list(parsed.get("alternatives", fallback.alternatives))
        fallback.chef_tip = parsed.get("chef_tip", fallback.chef_tip)
        fallback.nutrition_summary = parsed.get("nutrition_summary", fallback.nutrition_summary)
        return fallback

    def _build_intro(self, user_state) -> str:
        if user_state.goal == "learn":
            if user_state.challenge_level in {"hard", "expert"}:
                return "You want to learn something real, so I picked recipes that stretch your skills without ignoring your time and ingredients."
            return "You want to improve your cooking, so I picked recipes that teach useful techniques and still feel manageable."
        if user_state.goal == "gourmet":
            return "You asked for something more refined, so I chose recipes that feel restaurant-style and reward careful cooking."
        if user_state.goal == "explore":
            return "You wanted to explore, so I picked recipes that feel a little new while still fitting your ingredients and time."
        if user_state.goal == "convenience":
            return "You want convenience, so I kept the options simple, fast, and low-effort."
        if user_state.comfort_food:
            return "I hear you. Let's keep this warm, simple, and low-effort today."
        if user_state.energy_level == "high":
            return "Let's match your energy with something practical, fresh, and satisfying."
        if user_state.energy_level == "low":
            return "Let's keep cooking easy and pick something that still feels good to eat."
        return "I picked recipes that fit your ingredients, mood, and time without adding extra stress."

    @staticmethod
    def _build_nutrition_summary(recipe) -> str:
        nutrition = recipe.nutrition_per_serving or {}
        calories = nutrition.get("calories", "?")
        protein = nutrition.get("protein", "?")
        carbs = nutrition.get("carbs", "?")
        fat = nutrition.get("fat", "?")
        return f"Per serving: {calories} cal, {protein} protein, {carbs} carbs, {fat} fat."
