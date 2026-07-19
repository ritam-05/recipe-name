"""Main recipe agent class."""

from app.models.recipe import RecipeRecommendations
from app.services.recipe_service import RecipeService


class RecipeAgent:
    def __init__(self) -> None:
        self.recipe_service = RecipeService()

    def get_recipes(
        self,
        query_text: str,
        diet: str = "",
        time_limit: int = 0,
        servings: int = 2,
    ) -> RecipeRecommendations:
        return self.recipe_service.get_recipes(query_text, diet, time_limit, servings)
