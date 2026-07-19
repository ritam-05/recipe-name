"""Display helpers for recipes."""

from __future__ import annotations

from app.models.recipe import Recipe, RecipeRecommendations


def display_recommendations(result: RecipeRecommendations) -> None:
    if result.intro:
        print(result.intro)

    if result.why_selected:
        print("\nWhy these recipes were selected:")
        for reason in result.why_selected:
            print(f"  • {reason}")

    top_recipe = next((recipe for recipe in result.recipes if recipe.name == result.top_recommendation), None)
    if top_recipe is None and result.recipes:
        top_recipe = result.recipes[0]

    if top_recipe:
        ready_in = top_recipe.prep_time
        if top_recipe.total_minutes:
            ready_in = f"{top_recipe.total_minutes} minutes"
        print("\nWhy this recipe?")
        print(f"  {top_recipe.name} ({top_recipe.cuisine})")
        print(f"  Ready in {ready_in}")
        print(f"  Difficulty level: {top_recipe.difficulty_level}/5")
        print(f"  Learning value: {top_recipe.learning_value}/10")
        if top_recipe.why_it_fits:
            print("  Why this one:")
            for reason in top_recipe.why_it_fits[:3]:
                print(f"    - {reason}")

    if result.alternatives:
        print("\nAlternative recipes:")
        for recipe_name in result.alternatives:
            print(f"  • {recipe_name}")

    if result.chef_tip:
        print(f"\nChef tip: {result.chef_tip}")

    if result.nutrition_summary:
        print(f"Nutrition: {result.nutrition_summary}")

    if result.recipes:
        print("\nRecipes:")
        for recipe in result.recipes:
            display_recipe(recipe)
            print("\n" + "-" * 40)


def display_recipe(recipe: Recipe) -> None:
    print(f"\n🍽️  {recipe.name} ({recipe.cuisine})")
    print(
        f"⏱️  Prep: {recipe.prep_time} | Cook: {recipe.cook_time} | Difficulty: {recipe.difficulty}"
    )
    print(f"🎯 Difficulty level: {recipe.difficulty_level}/5 | Learning value: {recipe.learning_value}/10")
    if recipe.techniques:
        print(f"🛠️  Techniques: {', '.join(recipe.techniques)}")
    print(f"🧼 Cleanup: {recipe.estimated_cleanup}")
    if recipe.skill_tags:
        print(f"🏷️  Skill tags: {', '.join(recipe.skill_tags)}")
    print(f"👥 Serves: {recipe.servings}")
    print("\n📝 Ingredients:")
    for ingredient in recipe.ingredients_needed:
        print(f"  • {ingredient}")
    if recipe.missing_ingredients:
        print(f"\n➕ Optional additions: {', '.join(recipe.missing_ingredients)}")
    print("\n👨‍🍳 Instructions:")
    for index, step in enumerate(recipe.instructions, 1):
        if step.strip().lower().startswith("step "):
            print(f"  {step}")
        else:
            print(f"  Step {index}: {step}")
    if recipe.nutrition_per_serving:
        nutrition = recipe.nutrition_per_serving
        print(
            f"\n🥗 Nutrition: {nutrition.get('calories', '?')} cal | "
            f"Protein: {nutrition.get('protein', '?')} | "
            f"Carbs: {nutrition.get('carbs', '?')} | Fat: {nutrition.get('fat', '?')}"
        )
    if recipe.tips:
        print(f"\n💡 Chef's tip: {recipe.tips}")
