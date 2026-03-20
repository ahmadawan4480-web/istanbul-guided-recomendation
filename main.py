from recommendation.recommender import recommend_items
from llm.explanation_generator import generate_explanation

user_interests = ["history", "culture"]

results = recommend_items(user_interests)

print("Recommended Places and Events:\n")

for item in results:
    explanation = generate_explanation(item, user_interests)
    print(item["name"], "-", item["category"])
    print("Explanation:", explanation)
    print()