from pathlib import Path
import re
import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import linear_kernel

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

app = Flask(__name__)

# -----------------------------
# Load artifacts
# -----------------------------
rating_model = joblib.load(MODEL_DIR / "rating_model.pkl")
revenue_model = joblib.load(MODEL_DIR / "revenue_model.pkl")
success_model = joblib.load(MODEL_DIR / "success_classifier.pkl")

tfidf = joblib.load(MODEL_DIR / "movie_tfidf_vectorizer.pkl")
title_index = joblib.load(MODEL_DIR / "movie_title_index.pkl")
tfidf_matrix = load_npz(MODEL_DIR / "movie_tfidf_matrix.npz")
movies = pd.read_csv(MODEL_DIR / "movie_recommendation_data.csv")

# Keep the model artifacts aligned with the recommendation matrix.
movies["name"] = movies["name"].fillna("").astype(str).str.strip()
movies["search_name"] = movies["name"].str.lower()

def clean_text(value):
    return "" if pd.isna(value) else str(value).strip()

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value, default=0):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default

def normalize_title(title):
    return re.sub(r"\s+", " ", clean_text(title).lower()).strip()

def movie_card(row):
    return {
        "name": clean_text(row.get("name")),
        "genre": clean_text(row.get("genre")),
        "year": int(row["year"]) if pd.notna(row.get("year")) else None,
        "score": round(safe_float(row.get("score")), 1) if pd.notna(row.get("score")) else None,
        "votes": int(row["votes"]) if pd.notna(row.get("votes")) else None,
        "runtime": int(row["runtime"]) if pd.notna(row.get("runtime")) else None,
        "director": clean_text(row.get("director")),
        "country": clean_text(row.get("country")),
        "gross": round(safe_float(row.get("gross")), 0) if pd.notna(row.get("gross")) else None,
    }

@app.get("/")
def home():
    valid = movies[movies["name"].str.len() > 0]
    stats = {
        "movies": int(len(valid)),
        "genres": int(valid["genre"].nunique()),
        "directors": int(valid["director"].nunique()),
        "countries": int(valid["country"].nunique()),
        "avg_score": round(valid["score"].mean(), 2),
    }
    featured = (
        valid.sort_values("score", ascending=False)
        .head(8)
        .apply(movie_card, axis=1)
        .tolist()
    )
    return render_template("index.html", stats=stats, featured=featured)

@app.get("/api/search")
def search():
    query = normalize_title(request.args.get("q", ""))
    if not query:
        return jsonify([])

    mask = movies["search_name"].str.contains(re.escape(query), regex=True, na=False)
    results = movies.loc[mask].head(12)
    return jsonify([movie_card(row) for _, row in results.iterrows()])

@app.post("/api/recommend")
def recommend():
    payload = request.get_json(silent=True) or {}
    title = normalize_title(payload.get("title"))
    n = min(max(safe_int(payload.get("n"), 8), 1), 12)

    if not title:
        return jsonify({"error": "Please enter a movie title."}), 400

    # Exact match first. The saved index stores normalized title -> row position.
    row_idx = None
    if title in title_index.index:
        row_idx = int(title_index.loc[title])
    else:
        matches = movies.index[movies["search_name"].str.contains(re.escape(title), regex=True, na=False)]
        if len(matches):
            row_idx = int(matches[0])

    if row_idx is None or row_idx >= tfidf_matrix.shape[0]:
        return jsonify({"error": f"No movie found for '{payload.get('title', '')}'."}), 404

    similarities = linear_kernel(tfidf_matrix[row_idx], tfidf_matrix).ravel()
    similarities[row_idx] = -1
    top_indices = np.argsort(similarities)[::-1][:n]

    recommendations = []
    for idx in top_indices:
        if similarities[idx] < 0:
            continue
        card = movie_card(movies.iloc[idx])
        card["similarity"] = round(float(similarities[idx]), 3)
        recommendations.append(card)

    selected = movie_card(movies.iloc[row_idx])
    return jsonify({"selected": selected, "recommendations": recommendations})

@app.post("/api/predict/rating")
def predict_rating():
    data = request.get_json(silent=True) or {}
    row = {
        "year": safe_float(data.get("year")),
        "runtime": safe_float(data.get("runtime")),
        "release_year": safe_float(data.get("release_year") or data.get("year")),
        "genre": clean_text(data.get("genre")),
        "rating": clean_text(data.get("rating")),
        "country": clean_text(data.get("country")),
        "release_month": clean_text(data.get("release_month")),
    }
    prediction = float(rating_model.predict(pd.DataFrame([row]))[0])
    return jsonify({"prediction": round(float(np.clip(prediction, 0, 10)), 2)})

@app.post("/api/predict/revenue")
def predict_revenue():
    data = request.get_json(silent=True) or {}
    row = {
        "year": safe_float(data.get("year")),
        "score": safe_float(data.get("score")),
        "votes": safe_float(data.get("votes")),
        "budget": safe_float(data.get("budget")),
        "runtime": safe_float(data.get("runtime")),
        "release_year": safe_float(data.get("release_year") or data.get("year")),
        "genre": clean_text(data.get("genre")),
        "rating": clean_text(data.get("rating")),
        "country": clean_text(data.get("country")),
        "release_month": clean_text(data.get("release_month")),
    }
    log_prediction = float(revenue_model.predict(pd.DataFrame([row]))[0])
    gross = max(0.0, float(np.expm1(log_prediction)))
    return jsonify({"prediction": round(gross, 2), "formatted": f"${gross:,.0f}"})

@app.post("/api/predict/success")
def predict_success():
    data = request.get_json(silent=True) or {}
    row = {
        "year": safe_float(data.get("year")),
        "runtime": safe_float(data.get("runtime")),
        "release_year": safe_float(data.get("release_year") or data.get("year")),
        "genre": clean_text(data.get("genre")),
        "rating": clean_text(data.get("rating")),
        "country": clean_text(data.get("country")),
        "release_month": clean_text(data.get("release_month")),
    }
    prediction = int(success_model.predict(pd.DataFrame([row]))[0])
    probability = None
    if hasattr(success_model, "predict_proba"):
        probability = float(success_model.predict_proba(pd.DataFrame([row]))[0][1])
    return jsonify({
        "prediction": prediction,
        "label": "High audience score" if prediction else "Below high-score threshold",
        "probability": round(probability, 3) if probability is not None else None,
    })

if __name__ == "__main__":
    app.run(debug=True)
