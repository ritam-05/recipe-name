"""Intent and user-state extraction from the raw user query."""

from __future__ import annotations

from app.models.emotion import EmotionInference
from app.models.user_state import UserState
from app.services.emotion_service import EmotionService
from app.utils.helpers import extract_ingredients_from_request, extract_time_limit_from_request, normalize_text


class IntentService:
    def __init__(self) -> None:
        self.emotion_service = EmotionService()

    def build_user_state(
        self,
        query_text: str,
        diet: str = "",
        time_limit: int = 0,
        servings: int = 2,
    ) -> UserState:
        emotion_inference = self.emotion_service.infer_emotions(query_text)
        primary_profile = self.emotion_service.get_profile_by_emotion(emotion_inference.primary_emotion)
        secondary_profile = (
            self.emotion_service.get_profile_by_emotion(emotion_inference.secondary_emotion)
            if emotion_inference.secondary_emotion
            else None
        )

        ingredients = extract_ingredients_from_request(query_text)
        parsed_time_limit = extract_time_limit_from_request(query_text)
        effective_time_limit = time_limit or parsed_time_limit

        goal = self._infer_goal(query_text)
        challenge_level = self._infer_challenge_level(query_text, goal, effective_time_limit)
        effort_level = self._infer_effort_level(query_text, goal, effective_time_limit)

        preferred_tastes = self._infer_preferred_tastes(query_text, emotion_inference)
        if primary_profile.food_preferences:
            preferred_tastes.extend(self._map_preferences_to_tastes(primary_profile.food_preferences))
        if secondary_profile and secondary_profile.food_preferences:
            preferred_tastes.extend(self._map_preferences_to_tastes(secondary_profile.food_preferences))

        comfort_food = self._infer_comfort_food(emotion_inference)
        energy_level = self._infer_energy_level(query_text, emotion_inference)
        cooking_effort = self._infer_cooking_effort(query_text, emotion_inference, effective_time_limit)
        health_priority = self._infer_health_priority(query_text)
        budget = self._infer_budget(query_text)
        meal_type = self._infer_meal_type(query_text, emotion_inference)
        spice_level = self._infer_spice_level(query_text, emotion_inference)

        return UserState(
            query_text=query_text,
            primary_emotion=emotion_inference.primary_emotion,
            secondary_emotion=emotion_inference.secondary_emotion,
            confidence=emotion_inference.confidence,
            goal=goal,
            challenge_level=challenge_level,
            effort_level=effort_level,
            available_ingredients=ingredients,
            comfort_food=comfort_food,
            energy_level=energy_level,
            cooking_effort=cooking_effort,
            time_available=effective_time_limit,
            health_priority=health_priority,
            budget=budget,
            preferred_tastes=self._dedupe(preferred_tastes),
            meal_type=meal_type,
            spice_level=spice_level,
            ingredients=ingredients,
            diet=diet.strip(),
            servings=servings,
            preference_inspirations=self._dedupe(primary_profile.food_preferences + (
                secondary_profile.food_preferences if secondary_profile else []
            )),
        )

    def _infer_goal(self, query_text: str) -> str:
        normalized = normalize_text(query_text)

        if any(phrase in normalized for phrase in ("improve my cooking", "learn", "practice", "teach me", "technique", "master")):
            return "learn"
        if any(phrase in normalized for phrase in ("challenging", "hard", "difficult", "complex", "advanced", "expert", "technical")):
            return "learn"
        if any(phrase in normalized for phrase in ("restaurant-quality", "gourmet", "fine dining", "impressive", "fancy")):
            return "gourmet"
        if any(phrase in normalized for phrase in ("surprise me", "explore", "adventurous", "something different", "new cuisine")):
            return "explore"
        if any(phrase in normalized for phrase in ("lazy", "don't feel like cooking", "no effort", "convenient", "easy", "simple", "quick")):
            return "convenience"
        if any(phrase in normalized for phrase in ("comfort", "cozy", "soothing", "comfort food", "warm")):
            return "comfort"
        return "balance"

    def _infer_challenge_level(self, query_text: str, goal: str, time_available: int) -> str:
        normalized = normalize_text(query_text)
        if goal == "learn" and any(word in normalized for word in ("expert", "advanced", "master", "technical", "complex")):
            return "expert"
        if goal == "gourmet":
            return "hard"
        if goal == "explore":
            return "medium"
        if goal == "convenience":
            return "very_easy"
        if time_available >= 180:
            return "hard"
        if time_available >= 90:
            return "medium"
        if time_available and time_available <= 20:
            return "easy"
        if any(word in normalized for word in ("challenging", "hard", "difficult", "complex", "advanced", "expert")):
            return "hard"
        return "medium"

    def _infer_effort_level(self, query_text: str, goal: str, time_available: int) -> str:
        normalized = normalize_text(query_text)
        if goal == "convenience" or any(word in normalized for word in ("lazy", "minimal effort", "bare minimum", "easy", "quick")):
            return "minimal"
        if goal in {"learn", "gourmet"}:
            return "high"
        if time_available >= 180:
            return "high"
        if time_available >= 90:
            return "medium"
        if time_available and time_available <= 20:
            return "minimal"
        return "medium"

    def _infer_comfort_food(self, emotion_inference: EmotionInference) -> bool:
        comfort_emotions = {
            "heartbroken",
            "sad",
            "lonely",
            "nostalgic",
            "cozy",
            "sick",
            "tired",
            "lazy",
        }
        return any(emotion in comfort_emotions for emotion in emotion_inference.matched_emotions)

    def _infer_energy_level(self, query_text: str, emotion_inference: EmotionInference) -> str:
        normalized = normalize_text(query_text)
        low_energy = {"tired", "sad", "heartbroken", "sick", "lazy", "lonely", "cozy"}
        high_energy = {"energetic", "celebratory", "happy", "adventurous"}
        if any(emotion in low_energy for emotion in emotion_inference.matched_emotions):
            return "low"
        if any(emotion in high_energy for emotion in emotion_inference.matched_emotions):
            return "high"
        if any(word in normalized for word in ("after work", "exhausted", "no energy", "drained")):
            return "low"
        if any(word in normalized for word in ("workout", "gym", "study", "productive", "focused")):
            return "high"
        return "medium"

    def _infer_cooking_effort(self, query_text: str, emotion_inference: EmotionInference, time_available: int) -> str:
        normalized = normalize_text(query_text)
        if any(word in normalized for word in ("don't feel like cooking", "no energy to cook", "lazy", "quick", "easy")):
            return "minimal"
        if time_available and time_available <= 15:
            return "minimal"
        if time_available and time_available <= 30:
            return "low"
        if any(emotion in {"sick", "tired", "heartbroken", "lonely"} for emotion in emotion_inference.matched_emotions):
            return "minimal"
        return "medium"

    def _infer_health_priority(self, query_text: str) -> str:
        normalized = normalize_text(query_text)
        if any(word in normalized for word in ("healthy", "low calorie", "high protein", "nutrition", "light meal", "fit")):
            return "high"
        if any(word in normalized for word in ("balanced", "clean", "fresh", "wholesome")):
            return "medium"
        return "low"

    def _infer_budget(self, query_text: str) -> str:
        normalized = normalize_text(query_text)
        if any(word in normalized for word in ("cheap", "budget", "affordable", "save money", "inexpensive")):
            return "low"
        if any(word in normalized for word in ("fancy", "premium", "date night", "luxury")):
            return "high"
        return "medium"

    def _infer_meal_type(self, query_text: str, emotion_inference: EmotionInference) -> str:
        normalized = normalize_text(query_text)
        if any(word in normalized for word in ("breakfast", "morning", "brunch")):
            return "breakfast"
        if any(word in normalized for word in ("lunch", "midday", "work lunch")):
            return "lunch"
        if any(word in normalized for word in ("dessert", "sweet", "cake", "brownie", "ice cream")):
            return "dessert"
        if any(word in normalized for word in ("snack", "small bite", "appetizer")):
            return "snack"
        if any(emotion in {"heartbroken", "sad", "lonely", "cozy", "sick"} for emotion in emotion_inference.matched_emotions):
            return "soup"
        if any(emotion in {"celebratory", "happy"} for emotion in emotion_inference.matched_emotions):
            return "dinner"
        return "main"

    def _infer_spice_level(self, query_text: str, emotion_inference: EmotionInference) -> str:
        normalized = normalize_text(query_text)
        if any(word in normalized for word in ("very spicy", "extra hot", "fiery", "spicy")):
            return "hot"
        if any(word in normalized for word in ("mild", "gentle", "lightly spiced", "not spicy")):
            return "mild"
        if any(emotion in {"angry", "bored", "adventurous"} for emotion in emotion_inference.matched_emotions):
            return "medium"
        return "mild"

    def _infer_preferred_tastes(self, query_text: str, emotion_inference: EmotionInference) -> list[str]:
        normalized = normalize_text(query_text)
        tastes = []

        if any(word in normalized for word in ("sweet", "dessert", "brownie", "cake", "cookie", "chocolate")):
            tastes.append("sweet")
        if any(word in normalized for word in ("warm", "hot", "soup", "cozy", "comfort")):
            tastes.append("warm")
        if any(word in normalized for word in ("comfort", "creamy", "rich", "pasta", "ramen", "mac and cheese")):
            tastes.append("comforting")
        if any(word in normalized for word in ("fresh", "light", "salad", "fruit", "clean")):
            tastes.append("fresh")
        if any(word in normalized for word in ("spicy", "hot", "fiery")):
            tastes.append("spicy")
        if any(word in normalized for word in ("savory", "umami", "garlic", "rosemary", "herb")):
            tastes.append("savory")
        if any(word in normalized for word in ("crunchy", "crispy", "toasted")):
            tastes.append("crunchy")

        emotion_preferences = {
            "heartbroken": ["sweet", "warm", "comforting", "rich"],
            "sad": ["sweet", "warm", "comforting", "rich"],
            "stressed": ["warm", "light", "soothing", "balanced"],
            "anxious": ["warm", "mild", "soothing", "light"],
            "angry": ["spicy", "bold", "crunchy"],
            "bored": ["bold", "fun", "crunchy", "savory"],
            "romantic": ["rich", "sweet", "elegant"],
            "tired": ["warm", "simple", "filling"],
            "sick": ["warm", "mild", "gentle"],
            "nostalgic": ["warm", "homey", "sweet", "familiar"],
            "lonely": ["warm", "comforting", "rich"],
            "celebratory": ["festive", "sweet", "fun"],
            "adventurous": ["bold", "spicy", "tangy"],
            "focused": ["balanced", "light", "protein-rich"],
            "lazy": ["easy", "simple", "warm"],
            "energetic": ["fresh", "light", "protein-rich"],
            "guilty": ["light", "fresh", "balanced"],
            "curious": ["bold", "interesting", "new"],
            "cozy": ["warm", "soft", "comforting"],
            "happy": ["fun", "bright", "festive"],
        }

        for emotion in emotion_inference.matched_emotions:
            tastes.extend(emotion_preferences.get(emotion, []))

        return tastes

    def _map_preferences_to_tastes(self, preferences: list[str]) -> list[str]:
        taste_map = {
            "dessert": "sweet",
            "ice cream": "sweet",
            "cake": "sweet",
            "chocolate": "sweet",
            "brownies": "sweet",
            "hot chocolate": "sweet",
            "pasta": "comforting",
            "mac and cheese": "comforting",
            "soup": "warm",
            "ramen": "warm",
            "tea": "soothing",
            "mocktails": "bright",
            "pizza": "savory",
            "burgers": "savory",
            "sushi": "fresh",
            "salad": "fresh",
            "smoothies": "fresh",
            "wraps": "light",
            "yogurt": "light",
            "spicy noodles": "spicy",
            "street food": "bold",
            "fusion cuisine": "bold",
        }

        mapped = []
        for preference in preferences:
            lowered = preference.lower()
            if lowered in taste_map:
                mapped.append(taste_map[lowered])
        return mapped

    @staticmethod
    def _dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for item in items:
            normalized = item.strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            deduped.append(item)
        return deduped
