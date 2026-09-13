"""Small sample dataset used only by the mock agents for local testing."""

SAMPLE_RECIPES = [
    {
        "recipe_id": "r1",
        "title": "Grilled Chicken & Quinoa Bowl",
        "calories": 480,
        "protein_g": 38,
        "diet_tags": ["dairy-free", "gluten-free"],
        "ingredients": ["chicken breast", "quinoa", "broccoli", "olive oil"],
    },
    {
        "recipe_id": "r2",
        "title": "Tofu Stir Fry",
        "calories": 410,
        "protein_g": 22,
        "diet_tags": ["vegan", "dairy-free"],
        "ingredients": ["tofu", "soy sauce", "peppers", "rice"],
    },
    {
        "recipe_id": "r3",
        "title": "Lentil Dahl",
        "calories": 350,
        "protein_g": 18,
        "diet_tags": ["vegan", "gluten-free", "dairy-free"],
        "ingredients": ["lentils", "tomato", "spices"],
    },
    {
        "recipe_id": "r4",
        "title": "Creamy Mushroom Pasta",
        "calories": 620,
        "protein_g": 16,
        "diet_tags": ["vegetarian"],
        "ingredients": ["pasta", "cream", "mushroom", "parmesan"],
    },
    {
        "recipe_id": "r5",
        "title": "Turkey Chili",
        "calories": 470,
        "protein_g": 34,
        "diet_tags": ["dairy-free"],
        "ingredients": ["turkey", "beans", "tomato"],
    },
]

FAKE_REVIEWS = {
    "r1": {
        "sentiment_score": 0.7,
        "sentiment_label": "positive",
        "aspects": {"texture": "positive", "taste": "positive"},
        "summary": "Reviewers liked the juicy texture and balanced flavor.",
    },
    "r2": {
        "sentiment_score": 0.4,
        "sentiment_label": "positive",
        "aspects": {"texture": "mixed", "taste": "positive"},
        "summary": "Good flavor overall; some found the tofu texture a bit soft.",
    },
    "r3": {
        "sentiment_score": 0.6,
        "sentiment_label": "positive",
        "aspects": {"texture": "positive", "spice": "positive"},
        "summary": "Comforting and well-spiced with a consistent texture.",
    },
    "r4": {
        "sentiment_score": -0.1,
        "sentiment_label": "neutral",
        "aspects": {"texture": "positive", "richness": "negative"},
        "summary": "Nice creamy texture but several reviewers found it too rich.",
    },
    "r5": {
        "sentiment_score": 0.5,
        "sentiment_label": "positive",
        "aspects": {"texture": "positive", "spice": "mixed"},
        "summary": "Hearty texture; some reviewers wanted more spice.",
    },
}
