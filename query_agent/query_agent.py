import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# --- Simple stopword list for extracting meaningful search keywords ---
STOPWORDS = {
    "a", "an", "the", "is", "are", "for", "with", "of", "in", "on", "at",
    "to", "and", "or", "i", "me", "my", "have", "has", "want", "need",
    "please", "give", "some", "that", "this", "it", "be", "can", "you",
    "no", "not", "under", "over", "calories", "calorie"
}


def extract_keywords(user_query: str) -> list:
    """
    Extracts meaningful search terms from the query for TF-IDF matching.
    Removes stopwords and numbers, keeps real content words (food terms,
    ingredients, descriptive words) so the Retrieval Agent has actual text
    to run cosine similarity against.
    """
    words = re.findall(r'[a-zA-Z-]+', user_query.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]
    return keywords


def extract_constraints(user_query: str) -> dict:
    query_lower = user_query.lower()
    constraints = {}

    calorie_match = re.search(r'(\d+)\s*calor', query_lower)
    if calorie_match:
        constraints["max_calories"] = int(calorie_match.group(1))

    diets = []
    exclude_ingredients = []
    if "no dairy" in query_lower or "dairy-free" in query_lower or "dairy free" in query_lower:
        exclude_ingredients.append("dairy")
    if "vegan" in query_lower:
        diets.append("vegan")
    if "vegetarian" in query_lower:
        diets.append("vegetarian")
    if "gluten-free" in query_lower or "gluten free" in query_lower:
        diets.append("gluten-free")
        exclude_ingredients.append("gluten")

    if "high-protein" in query_lower or "high protein" in query_lower:
        constraints["min_protein_g"] = 20

    for meal in ["breakfast", "lunch", "dinner", "snack", "dessert"]:
        if meal in query_lower:
            constraints["meal_type"] = meal
            break

    # --- Start keywords with the real content words from the query ---
    keywords = extract_keywords(user_query)

    # --- Then layer on explicit category tags (still useful signal for search) ---
    time_match = re.search(r'under (\d+)\s*min', query_lower)
    if time_match:
        keywords.append(f"max_prep_time:{time_match.group(1)}")
    elif re.search(r'\bquick\b', query_lower) or re.search(r'\bfast\b', query_lower):
        keywords.append("quick")

    if "low sugar" in query_lower or "low-sugar" in query_lower or "diabetic" in query_lower:
        keywords.append("low_sugar")
    if "low sodium" in query_lower or "low-sodium" in query_lower:
        keywords.append("low_sodium")
    if "diabetic" in query_lower or "diabetes" in query_lower:
        keywords.append("diabetic_friendly")
    if "high blood pressure" in query_lower or "hypertension" in query_lower:
        keywords.append("heart_healthy")
    if "heart-healthy" in query_lower or "heart healthy" in query_lower:
        keywords.append("heart_healthy")

    if "bulk" in query_lower or "bulking" in query_lower or "muscle gain" in query_lower or "build muscle" in query_lower:
        keywords.append("bulking")
        constraints["min_protein_g"] = 20
    if "cut" in query_lower or "cutting" in query_lower or "weight loss" in query_lower or "lose weight" in query_lower or "fat loss" in query_lower:
        keywords.append("cutting")
        constraints["max_calories"] = constraints.get("max_calories", 400)
        constraints["min_protein_g"] = 20
    if "post-workout" in query_lower or "post workout" in query_lower:
        keywords.append("post_workout")
        constraints["min_protein_g"] = 20
    if "pre-workout" in query_lower or "pre workout" in query_lower:
        keywords.append("pre_workout")

    constraints["diet_tags"] = diets
    constraints["exclude_ingredients"] = exclude_ingredients
    keywords = list(dict.fromkeys(keywords))  # removes duplicates, keeps order
    constraints["keywords"] = keywords

    return constraints


def detect_intent(user_query: str) -> str:
    query_lower = user_query.lower()
    if any(p in query_lower for p in ["what do people say", "reviews", "is it good", "how does it taste"]):
        return "review_lookup"
    return "recommend_recipe"


def validate_query(user_query: str) -> tuple[bool, str]:
    if not user_query or not user_query.strip():
        return False, "Query cannot be empty"
    if len(user_query) > 500:
        return False, "Query is too long (max 500 characters)"
    suspicious_patterns = ["ignore previous", "system prompt", "<script"]
    query_lower = user_query.lower()
    for pattern in suspicious_patterns:
        if pattern in query_lower:
            return False, "Query contains disallowed content"
    return True, ""


app = FastAPI()


class QueryRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse")
def parse_query(request: QueryRequest):
    is_valid, error_message = validate_query(request.query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    extracted = extract_constraints(request.query)
    intent = detect_intent(request.query)

    return {
        "intent": intent,
        "diet_tags": extracted.get("diet_tags", []),
        "exclude_ingredients": extracted.get("exclude_ingredients", []),
        "max_calories": extracted.get("max_calories"),
        "min_protein_g": extracted.get("min_protein_g"),
        "meal_type": extracted.get("meal_type"),
        "keywords": extracted.get("keywords", []),
        "target_recipe_name": None
    }


if __name__ == "__main__":
    test_queries = [
        "high-protein dinner under 500 calories, no dairy",
        "vegan breakfast, gluten-free",
        "cutting diet, low calorie, low fat dinner",
        "spicy thai chicken curry with coconut milk",
    ]
    for q in test_queries:
        print("Query:", q)
        print("Constraints:", extract_constraints(q))
        print("Intent:", detect_intent(q))
        print("---")