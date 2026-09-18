"""
retrieval_agent/tests/test_retrieval.py

Basic correctness tests — run with:
    pytest tests/test_retrieval.py -v
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_200():
    response = client.post("/search", json={
        "intent": "recommend_recipe",
        "diet_tags": [],
        "exclude_ingredients": [],
        "max_calories": None,
        "min_protein_g": None,
        "meal_type": None,
        "keywords": ["chicken"],
        "target_recipe_name": None,
    })
    assert response.status_code == 200


def test_search_returns_results_list():
    response = client.post("/search", json={
        "intent": "recommend_recipe",
        "diet_tags": [],
        "exclude_ingredients": [],
        "max_calories": 500,
        "min_protein_g": 10,
        "meal_type": "dinner",
        "keywords": ["chickpea", "curry"],
        "target_recipe_name": None,
    })
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) <= 10


def test_dairy_exclusion():
    response = client.post("/search", json={
        "intent": "recommend_recipe",
        "diet_tags": [],
        "exclude_ingredients": ["dairy"],
        "max_calories": 800,
        "min_protein_g": 0,
        "meal_type": "dessert",
        "keywords": ["cheese", "cream", "cake"],
        "target_recipe_name": None,
    })
    results = response.json()["results"]
    dairy_terms = ["milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee"]
    for r in results:
        ingredients_text = " ".join(r["ingredients"]).lower()
        assert not any(term in ingredients_text for term in dairy_terms), \
            f"{r['title']} still contains a dairy ingredient"


def test_calorie_filter_respected():
    max_cal = 400
    response = client.post("/search", json={
        "intent": "recommend_recipe",
        "diet_tags": [],
        "exclude_ingredients": [],
        "max_calories": max_cal,
        "min_protein_g": None,
        "meal_type": None,
        "keywords": ["salad"],
        "target_recipe_name": None,
    })
    results = response.json()["results"]
    for r in results:
        if r["calories"] is not None:
            assert r["calories"] <= max_cal


def test_empty_keywords_does_not_crash():
    response = client.post("/search", json={
        "intent": "recommend_recipe",
        "diet_tags": [],
        "exclude_ingredients": [],
        "max_calories": None,
        "min_protein_g": None,
        "meal_type": None,
        "keywords": [],
        "target_recipe_name": None,
    })
    assert response.status_code == 200