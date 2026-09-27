import re
import pandas as pd
from fastapi import FastAPI
from schemas import ParsedConstraints, RetrievalResponse, RetrievedRecipe
from retriever import df, rank, query_text_from
from filters import apply_filters

app = FastAPI()


def parse_step_list(raw_value) -> list[str]:
    """Handles both c("step1", "step2") R-vector format and plain comma-separated text."""
    if pd.isna(raw_value) or not str(raw_value).strip():
        return []
    text = str(raw_value).strip()

    quoted = re.findall(r'"([^"]+)"', text)
    if quoted:
        return quoted

    # Steps were originally joined with ", " and each step already ends in
    # a period — so the real boundary between steps is ".," not just ",".
    # Splitting on plain ", " cuts through commas *inside* a step (e.g.
    # "blend butter, brown sugar and flour" becomes two fake steps).
    parts = re.split(r'\.,\s*', text)
    steps = []
    for p in parts:
        p = p.strip()
        if not p or p.lower() == "nan":
            continue
        if not p.endswith((".", "!", "?")):
            p += "."
        steps.append(p)
    return steps


@app.post("/search", response_model=RetrievalResponse)
def search(constraints: ParsedConstraints):
    filtered = apply_filters(df, constraints)
    query_text = query_text_from(constraints)
    ranked = rank(filtered, query_text, top_k=10)

    results = [
        RetrievedRecipe(
            recipe_id=str(row["RecipeId"]),
            title=row["Name"],
            score=score,
            calories=int(round(row["Calories"])) if pd.notna(row["Calories"]) else None,
            protein_g=int(round(row["ProteinContent"])) if pd.notna(row["ProteinContent"]) else None,
            diet_tags=constraints.diet_tags,
            ingredients=parse_step_list(row["RecipeIngredientParts"]),
            instructions=parse_step_list(row["RecipeInstructions"]),
            prep_time_minutes=int(row["PrepTimeMinutes"]) if pd.notna(row["PrepTimeMinutes"]) else None,
        )
        for row, score in ranked
    ]

    return RetrievalResponse(results=results, query_echo=query_text)


@app.get("/health")
def health():
    return {"status": "ok"}