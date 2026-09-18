"""
retrieval_agent/evaluate.py

Sends a handful of test queries to the running /search endpoint and scores
the results against manually judged "relevant" recipe IDs.

Run this while uvicorn is running on port 8002:
    python evaluate.py
"""
import requests


BASE_URL = "http://127.0.0.1:8002"

DAIRY_TERMS = ["milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee"]

TEST_CASES = [
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": ["vegan"],
            "exclude_ingredients": ["dairy"],
            "max_calories": 500,
            "min_protein_g": 15,
            "meal_type": "dinner",
            "keywords": ["chickpea", "curry"],
            "target_recipe_name": None,
        },
        "relevant_ids": ["460196", "312286", "197461"],
    },
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": [],
            "exclude_ingredients": [],
            "max_calories": 400,
            "min_protein_g": 20,
            "meal_type": "breakfast",
            "keywords": ["egg", "protein"],
            "target_recipe_name": None,
        },
        "relevant_ids": ["134470", "28042", "344050", "37363"],
    },
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": [],
            "exclude_ingredients": ["dairy"],
            "max_calories": 800,
            "min_protein_g": 0,
            "meal_type": "dessert",
            "keywords": ["cheese", "cream", "cake"],
            "target_recipe_name": None,
        },
        "relevant_ids": [],  # intentionally empty — this case tests exclude_ingredients, not ranking
    },
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": ["vegetable"],
            "exclude_ingredients": [],
            "max_calories": 600,
            "min_protein_g": 10,
            "meal_type": "lunch",
            "keywords": ["pasta", "tomato"],
            "target_recipe_name": None,
        },
        "relevant_ids": ["249128", "150358", "19044", "23624"],
    },
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": [],
            "exclude_ingredients": [],
            "max_calories": 450,
            "min_protein_g": 20,
            "meal_type": "dinner",
            "keywords": ["chicken", "grilled"],
            "target_recipe_name": None,
        },
        "relevant_ids": ["297408", "216417", "170690", "36928"],
    },
    {
        "constraints": {
            "intent": "recommend_recipe",
            "diet_tags": [],
            "exclude_ingredients": ["dairy"],
            "max_calories": 300,
            "min_protein_g": 10,
            "meal_type": "snack",
            "keywords": ["fruit", "smoothie"],
            "target_recipe_name": None,
        },
        # Intentionally empty — none of the retrieved results are genuinely relevant.
        # Notably, similarity scores here (0.03-0.05) are far lower than other queries
        # (0.13-0.34), correctly signaling low confidence rather than a ranking failure.
        "relevant_ids": [],
    },
]


def precision_at_k(retrieved_ids, relevant_ids, k):
    top_k = retrieved_ids[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / len(top_k)


def recall_at_k(retrieved_ids, relevant_ids, k):
    if not relevant_ids:
        return None
    top_k = retrieved_ids[:k]
    hits = sum(1 for rid in top_k if rid in relevant_ids)
    return hits / len(relevant_ids)


def reciprocal_rank(retrieved_ids, relevant_ids):
    for i, rid in enumerate(retrieved_ids, start=1):
        if rid in relevant_ids:
            return 1.0 / i
    return 0.0


def check_exclusion(results, excluded_category):
    terms = DAIRY_TERMS if excluded_category.lower() == "dairy" else [excluded_category]
    violations = []
    for r in results:
        ingredients_text = " ".join(r["ingredients"]).lower()
        if any(term in ingredients_text for term in terms):
            violations.append((r["recipe_id"], r["title"]))
    if violations:
        print(f"  ❌ FILTER FAILED — {len(violations)} result(s) still contain '{excluded_category}':")
        for rid, title in violations:
            print(f"     {rid}: {title}")
    else:
        print(f"  ✅ Filter working — no '{excluded_category}' found in {len(results)} results")


def run_evaluation(k=5):
    precisions, recalls, rr_scores = [], [], []

    for i, case in enumerate(TEST_CASES, start=1):
        response = requests.post(f"{BASE_URL}/search", json=case["constraints"])
        response.raise_for_status()
        results = response.json()["results"]
        retrieved_ids = [r["recipe_id"] for r in results]

        relevant_ids = set(case["relevant_ids"])

        p = precision_at_k(retrieved_ids, relevant_ids, k)
        r = recall_at_k(retrieved_ids, relevant_ids, k)
        rr = reciprocal_rank(retrieved_ids, relevant_ids)

        precisions.append(p)
        if r is not None:
            recalls.append(r)
        rr_scores.append(rr)

        print(f"Query {i}: {case['constraints']['keywords']}")
        print(f"  Retrieved: {retrieved_ids}")
        print(f"  Relevant:  {sorted(relevant_ids)}")
        print(f"  Precision@{k}: {p:.2f}")
        print(f"  Recall@{k}:    {'n/a (no relevant set)' if r is None else f'{r:.2f}'}")
        print(f"  Reciprocal rank: {rr:.2f}")

        if case["constraints"]["exclude_ingredients"]:
            for excl in case["constraints"]["exclude_ingredients"]:
                check_exclusion(results, excl)

        print()

    print("=" * 40)
    print(f"Mean Precision@{k}: {sum(precisions)/len(precisions):.3f}")
    if recalls:
        print(f"Mean Recall@{k}:    {sum(recalls)/len(recalls):.3f}")
    print(f"MRR:               {sum(rr_scores)/len(rr_scores):.3f}")


if __name__ == "__main__":
    run_evaluation(k=5)