"""Application entry point for the recipe agent"""

import argparse

from app.agents.recipe_agent import RecipeAgent
from app.utils.display import display_recommendations


def main() -> None:
    parser = argparse.ArgumentParser(description="Recipe Recommendation Agent")
    parser.add_argument(
        "--query",
        default="",
        help="Natural-language request describing your mood, ingredients, and time",
    )
    parser.add_argument(
        "--diet",
        default="",
        help="Dietary restriction (vegan, vegetarian, gluten-free, keto, etc.)",
    )
    parser.add_argument("--time", type=int, default=0, help="Max cooking time in minutes")
    parser.add_argument("--servings", type=int, default=2, help="Number of servings")
    args = parser.parse_args()

    if args.query:
        request_text = args.query
    else:
        request_text = input(
            'Describe what you feel and what ingredients you have, for example: "i am sad and i have chicken, garlic, lemon, rosemary, and 1 hour to cook": '
        ).strip()

    if not request_text:
        print("No request was provided.")
        return

    print(f"\n🥘 Understanding your request: {request_text}")
    if args.diet:
        print(f"🥗 Diet: {args.diet}")
    if args.time:
        print(f"⏱️  Max time: {args.time} minutes")

    agent = RecipeAgent()
    result = agent.get_recipes(request_text, args.diet, args.time, args.servings)

    print("\n" + "=" * 60)
    if result.matched_emotion:
        emotion_label = result.matched_emotion
        if result.secondary_emotion:
            emotion_label = f"{result.matched_emotion} + {result.secondary_emotion}"
        print(f"🎭 Emotion matched: {emotion_label} ({result.confidence:.2f})")
    if result.matched_preferences:
        print(f"🍲 Preference inspiration: {', '.join(result.matched_preferences[:5])}")
    print("=" * 60)

    display_recommendations(result)


if __name__ == "__main__":
    main()
