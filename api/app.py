from fastapi import FastAPI
from pydantic import BaseModel
from recommendation.recommender import recommend_items
from llm.explanation_generator import generate_explanation
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Istanbul Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRequest(BaseModel):
    interests: list[str]

@app.post("/recommend")
def get_recommendations(request: UserRequest):
    user_interests = request.interests
    results = recommend_items(user_interests)

    # Add LLM explanations
    for item in results:
        item["llm_explanation"] = generate_explanation(item, user_interests)

    return {"status": "success", "recommendations": results}