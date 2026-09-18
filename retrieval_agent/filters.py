"""
retrieval_agent/filters.py
"""
import pandas as pd
from schemas import ParsedConstraints

# Category-name -> actual ingredient words that appear in the data.
# Add more categories here (e.g. "nuts", "gluten") the same way if needed.
INGREDIENT_CATEGORY_TERMS = {
    "dairy": ["milk", "cheese", "butter", "cream", "yogurt", "yoghurt", "ghee","margarine"],
}


def apply_filters(df: pd.DataFrame, constraints: ParsedConstraints) -> pd.DataFrame:
    filtered = df.copy()

    if constraints.max_calories is not None:
        filtered = filtered[filtered["Calories"] <= constraints.max_calories]

    if constraints.min_protein_g is not None:
        filtered = filtered[filtered["ProteinContent"] >= constraints.min_protein_g]

    for tag in constraints.diet_tags:
        filtered = filtered[filtered["Keywords"].str.contains(tag, case=False, na=False)]

    for ingredient in constraints.exclude_ingredients:
        # If it's a known category name (like "dairy"), expand it into the
        # real ingredient words. Otherwise treat it as a literal ingredient.
        terms = INGREDIENT_CATEGORY_TERMS.get(ingredient.lower(), [ingredient])
        for term in terms:
            filtered = filtered[~filtered["RecipeIngredientParts"].str.contains(term, case=False, na=False)]

    return filtered