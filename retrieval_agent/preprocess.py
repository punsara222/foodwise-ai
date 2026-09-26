import pandas as pd
from duration_utils import parse_duration_to_minutes

df = pd.read_csv("../data/foodwise_final_dataset.csv")

df = df.drop_duplicates(subset="RecipeId", keep="first")

df["PrepTimeMinutes"] = df["PrepTime"].apply(parse_duration_to_minutes)

df["RecipeIngredientParts"] = df["RecipeIngredientParts"].fillna("")

df["Keywords"] = df["Keywords"].fillna("")
df["Name"] = df["Name"].fillna("")
df["RecipeInstructions"] = df["RecipeInstructions"].fillna("")
df["PrepTimeMinutes"] = df["PrepTimeMinutes"].fillna(0)

df.to_parquet("../data/recipes_clean.parquet")