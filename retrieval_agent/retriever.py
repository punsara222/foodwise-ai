"""
retrieval_agent/retriever.py
Loads the cleaned recipe data and builds the TF-IDF index once, at import time.
"""
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes_clean.parquet"
df = pd.read_parquet(DATA_PATH)

df = df.reset_index(drop=True)  # positions must line up with tfidf_matrix rows

# --- Build the TF-IDF index once ------------------------------------------
df["combined_text"] = (
    df["Name"].fillna("") + " " +
    df["Keywords"].fillna("") + " " +
    df["RecipeIngredientParts"].fillna("")
)
vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
tfidf_matrix = vectorizer.fit_transform(df["combined_text"].tolist())


def query_text_from(constraints) -> str:
    """Builds the text to rank against — prefers the raw query text if available."""
    if constraints.raw_query:
        return constraints.raw_query

    parts = list(constraints.keywords)
    if constraints.meal_type:
        parts.append(constraints.meal_type)
    parts.extend(constraints.diet_tags)
    return " ".join(parts)


def rank(filtered_df: pd.DataFrame, query_text: str, top_k: int = 10):
    """Returns a list of (row, score) tuples, best match first."""
    if not query_text.strip() or filtered_df.empty:
        return [(row, 0.0) for _, row in filtered_df.head(top_k).iterrows()]

    filtered_indices = filtered_df.index.tolist()
    query_vec = vectorizer.transform([query_text])
    sims = cosine_similarity(query_vec, tfidf_matrix[filtered_indices]).flatten()

    scored = sorted(zip(filtered_indices, sims), key=lambda x: -x[1])[:top_k]
    return [(df.loc[idx], float(score)) for idx, score in scored]