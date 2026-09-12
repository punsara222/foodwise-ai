import re

def extract_constraints(user_query: str) -> dict:
    query_lower = user_query.lower()
    constraints = {}

    calorie_match = re.search(r'(\d+)\s*calor', query_lower)
    if calorie_match:
        constraints["max_calories"] = int(calorie_match.group(1))

    diets = []
    if "no dairy" in query_lower or "dairy-free" in query_lower or "dairy free" in query_lower:
        diets.append("dairy-free")
    if "vegan" in query_lower:
        diets.append("vegan")
    if "vegetarian" in query_lower:
        diets.append("vegetarian")
    if "gluten-free" in query_lower or "gluten free" in query_lower:
        diets.append("gluten-free")
    if diets:
        constraints["diet"] = diets

    if "high-protein" in query_lower or "high protein" in query_lower:
        constraints["min_protein"] = "high"

    for meal in ["breakfast", "lunch", "dinner", "snack", "dessert"]:
        if meal in query_lower:
            constraints["meal_type"] = meal
            break

    time_match = re.search(r'under (\d+)\s*min', query_lower)
    if time_match:
        constraints["max_prep_time_minutes"] = int(time_match.group(1))
    elif re.search(r'\bquick\b', query_lower) or re.search(r'\bfast\b', query_lower):
        constraints["max_prep_time_minutes"] = 30

    if "low sugar" in query_lower or "low-sugar" in query_lower or "diabetic" in query_lower:
        constraints["max_sugar"] = "low"

    if "low sodium" in query_lower or "low-sodium" in query_lower:
        constraints["max_sodium"] = "low"

    if "diabetic" in query_lower or "diabetes" in query_lower:
        constraints["health_flag"] = "diabetic-friendly"
        constraints["max_sugar"] = "low"

    if "high blood pressure" in query_lower or "hypertension" in query_lower:
        constraints["health_flag"] = "heart-healthy"
        constraints["max_sodium"] = "low"

    if "heart-healthy" in query_lower or "heart healthy" in query_lower:
        constraints["health_flag"] = "heart-healthy"

    # --- Fitness/gym-related goals ---
    if "bulk" in query_lower or "bulking" in query_lower or "muscle gain" in query_lower or "build muscle" in query_lower:
        constraints["fitness_goal"] = "bulking"
        constraints["min_protein"] = "high"
        constraints["min_calories"] = 500

    if "cut" in query_lower or "cutting" in query_lower or "weight loss" in query_lower or "lose weight" in query_lower or "fat loss" in query_lower:
        constraints["fitness_goal"] = "cutting"
        constraints["max_calories"] = constraints.get("max_calories", 400)
        constraints["min_protein"] = "high"
        constraints["max_fat"] = "low"

    if "post-workout" in query_lower or "post workout" in query_lower or "after gym" in query_lower or "after workout" in query_lower:
        constraints["fitness_goal"] = "post-workout"
        constraints["min_protein"] = "high"

    if "pre-workout" in query_lower or "pre workout" in query_lower or "before gym" in query_lower:
        constraints["fitness_goal"] = "pre-workout"
        constraints["max_fat"] = "low"

    return constraints


if __name__ == "__main__":
    test_queries = [
        "high-protein dinner under 500 calories, no dairy",
        "vegan breakfast, gluten-free",
        "quick lunch under 300 calories",
        "low sugar dessert for a diabetic-friendly diet",
        "heart-healthy dinner, low sodium, I have high blood pressure",
        "high calorie bulking meal with lots of protein",
        "post-workout snack, high protein",
        "cutting diet, low calorie, low fat dinner",
    ]

    for q in test_queries:
        result = extract_constraints(q)
        print("Query:", q)
        print("Extracted constraints:", result)
        print("---")