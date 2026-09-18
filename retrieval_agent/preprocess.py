import pandas as pd
from duration_utils import parse_duration_to_minutes

df = pd.read_csv("../data/foodwise_final_dataset.csv")

# Collapse review-joined rows down to one row per recipe.
# keep="first" just picks whichever copy appears first — fine since every
# duplicate row has identical recipe-level fields, only the review columns differ.
df = df.drop_duplicates(subset="RecipeId", keep="first")

df["PrepTimeMinutes"] = df["PrepTime"].apply(parse_duration_to_minutes)

# Replace missing ingredient text with an empty string instead of NaN,
# so it doesn't get stringified into the literal text "nan" later.
df["RecipeIngredientParts"] = df["RecipeIngredientParts"].fillna("")

# Same treatment for other text columns your retriever/filters touch,
# so none of them can produce a stray "nan" string either.
df["Keywords"] = df["Keywords"].fillna("")
df["Name"] = df["Name"].fillna("")

df.to_parquet("../data/recipes_clean.parquet")