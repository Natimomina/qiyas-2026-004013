"""Train and compare baseline sentiment classifiers."""
from pathlib import Path
import json
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.metrics import (accuracy_score, precision_recall_fscore_support,
                             classification_report, confusion_matrix)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
FIG_DIR = REPORT_DIR / "figures"
for folder in (MODEL_DIR, REPORT_DIR, FIG_DIR):
    folder.mkdir(parents=True, exist_ok=True)

def load_dataset():
    frames = []
    for filename in ("one.txt", "two.txt", "three.txt"):
        path = RAW_DIR / filename
        frame = pd.read_csv(path, sep="\t", names=["text", "label"],
                            quoting=3, encoding="utf-8", on_bad_lines="skip")
        frame["source"] = path.stem
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    data["text"] = data["text"].fillna("").astype(str).str.strip()
    data = data[(data["text"] != "") & data["label"].isin([0, 1])]
    return data.drop_duplicates(subset=["text", "label"]).reset_index(drop=True)

def make_vectorizer():
    return TfidfVectorizer(ngram_range=(1, 2), min_df=2,
                           max_features=50000, sublinear_tf=True,
                           strip_accents="unicode")

def main():
    data = load_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        data["text"], data["label"], test_size=0.2,
        random_state=42, stratify=data["label"])
    candidates = {
        "Logistic Regression": Pipeline([
            ("tfidf", make_vectorizer()),
            ("classifier", LogisticRegression(max_iter=1500, C=2.0))]),
        "Linear SVM": Pipeline([
            ("tfidf", make_vectorizer()),
            ("classifier", LinearSVC(C=1.0))]),
        "Multinomial Naive Bayes": Pipeline([
            ("tfidf", make_vectorizer()),
            ("classifier", MultinomialNB(alpha=0.5))]),
    }
    rows, fitted = [], {}
    for name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        prediction = pipeline.predict(X_test)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, prediction, average="binary", zero_division=0)
        rows.append({"model": name, "accuracy": accuracy_score(y_test, prediction),
                     "precision": precision, "recall": recall, "f1": f1})
        fitted[name] = pipeline
        print(f"{name}: accuracy={accuracy_score(y_test, prediction):.3f}, F1={f1:.3f}")
    comparison = pd.DataFrame(rows).sort_values("f1", ascending=False)
    best_name = comparison.iloc[0]["model"]
    best_model = fitted[best_name]
    prediction = best_model.predict(X_test)
    report = classification_report(y_test, prediction,
                                   target_names=["Negative", "Positive"],
                                   output_dict=True, zero_division=0)
    joblib.dump(best_model, MODEL_DIR / "sentiment_pipeline.joblib")
    comparison.to_csv(REPORT_DIR / "model_comparison.csv", index=False)
    metrics = {
        "best_model": best_name,
        "dataset": {"rows": int(len(data)),
                    "positive": int((data.label == 1).sum()),
                    "negative": int((data.label == 0).sum()),
                    "train_rows": int(len(X_train)), "test_rows": int(len(X_test))},
        "best_model_metrics": {
            "accuracy": float(accuracy_score(y_test, prediction)),
            "precision": float(report["Positive"]["precision"]),
            "recall": float(report["Positive"]["recall"]),
            "f1": float(report["Positive"]["f1-score"])},
        "classification_report": report,
        "model_comparison": comparison.to_dict("records"),
        "label_mapping": {"0": "Negative", "1": "Positive"}}
    (REPORT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    cm = confusion_matrix(y_test, prediction)
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    image = ax.imshow(cm, cmap="Blues")
    ax.set(xticks=[0, 1], xticklabels=["Negative", "Positive"],
           yticks=[0, 1], yticklabels=["Negative", "Positive"],
           xlabel="Predicted label", ylabel="Actual label",
           title="Confusion matrix")
    for (row, col), value in __import__("numpy").ndenumerate(cm):
        ax.text(col, row, str(value), ha="center", va="center")
    fig.colorbar(image, ax=ax, fraction=.046, pad=.04)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "confusion_matrix.png", dpi=160)
    plt.close(fig)
    print(f"\\nSaved best model: {best_name}")
    print(f"Reports saved in: {REPORT_DIR}")

if __name__ == "__main__":
    main()
