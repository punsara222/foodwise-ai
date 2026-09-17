import pandas as pd
from fastapi import FastAPI
from schemas import ParsedConstraints, RetrievalResponse, RetrievedRecipe
from retriever import df, rank, query_text_from
from filters import apply_filters

app = FastAPI()


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
            ingredients=[i for i in str(row["RecipeIngredientParts"]).split(", ") if i and i.lower() != "nan"],
        )
        for row, score in ranked
    ]

    return RetrievalResponse(results=results, query_echo=query_text)


@app.get("/health")
def health():
    return {"status": "ok"}