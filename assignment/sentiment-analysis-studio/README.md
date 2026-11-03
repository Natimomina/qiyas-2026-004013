# Sentiment Analysis Studio

A complete, beginner-friendly sentiment analysis project and its three text data files. It includes a reproducible modeling notebook, a training script, saved model, evaluation reports, and a Streamlit web app.

## Preview

The app provides:
- A live text sentiment analyzer (positive / negative)
- Quick sample sentences
- Model performance and comparison dashboard
- Project methodology and limitations

## Project results

The cleaned dataset contains **2,982 unique text/label rows** after removing exact duplicate text/label pairs.

| Metric | Value |
|---|---:|
| Positive examples | 1,490 |
| Negative examples | 1,492 |
| Training examples | 2,385 |
| Held-out test examples | 597 |
| Selected model | Multinomial Naive Bayes |
| Test accuracy | 81.4% |
| Test precision | 81.1% |
| Test recall | 81.9% |
| Test F1-score | 81.5% |

These are results from a single stratified 80/20 split (`random_state=42`), not a guarantee of performance on every new dataset.

## Folder structure

```text
sentiment-analysis-studio/
├── app.py                          # Streamlit user interface
├── requirements.txt                # Python dependencies
├── README.md                       # Setup and project documentation
├── data/
│   └── raw/
│       ├── one.txt                 # Original source file 1
│       ├── two.txt                 # Original source file 2
│       └── three.txt               # Original source file 3
├── models/
│   └── sentiment_pipeline.joblib   # Trained TF-IDF + classifier pipeline
├── notebooks/
│   ├── Sentiment_Analysis_Walkthrough.ipynb
│   └── Sentiment_modeling_Qiyas_original.ipynb
├── reports/
│   ├── metrics.json
│   ├── model_comparison.csv
│   └── figures/
│       └── confusion_matrix.png
└── src/
    └── train.py                    # Re-train and regenerate reports
```

## 1. Requirements

- Python 3.9 or newer
- pip
- Recommended: a virtual environment

## 2. Install

Open a terminal in this project folder.

### Windows (PowerShell / CMD)

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Run the web application

```bash
streamlit run app.py
```

Streamlit will print a local URL (normally `http://localhost:8501`). Open it in your browser.

The saved model and metrics are included, so you do not need to train the model before launching the app.

## 4. Retrain the model

If you change the source data or want to reproduce the training process:

```bash
python src/train.py
```

The script:
1. Loads all three raw text files.
2. Removes empty rows and exact duplicate text/label pairs.
3. Creates a stratified 80/20 train/test split.
4. Trains Logistic Regression, Linear SVM, and Multinomial Naive Bayes using TF-IDF features.
5. Selects the model with the highest test F1-score.
6. Saves the selected pipeline to `models/` and evaluation files to `reports/`.

## 5. Open the notebook

Launch Jupyter from the project directory:

```bash
jupyter notebook
```

Open `notebooks/Sentiment_Analysis_Walkthrough.ipynb` and run the cells from top to bottom. The original Qiyas notebook is also preserved as a reference.

## Methodology

- **Labels:** `0 = Negative`, `1 = Positive`
- **Text features:** TF-IDF with unigrams and bigrams
- **Split:** 80% train, 20% test, stratified, fixed random seed
- **Models compared:** Logistic Regression, Linear SVM, Multinomial Naive Bayes
- **Selection:** highest F1-score on the held-out test set

The text vectorizer and classifier are stored together in one scikit-learn pipeline. The app therefore accepts raw text and applies the same preprocessing used during training.

## Limitations

- The task is binary; there is no neutral class.
- The original data is English-language review text. Do not assume the model supports Amharic or other languages.
- Sentiment can be ambiguous. Sarcasm, slang, mixed opinions, and context-dependent wording may lead to incorrect predictions.
- The score shown by the app is a model probability estimate, not a guarantee that the prediction is correct.
- The held-out test set comes from the same combined collection as the training data. Evaluation on a new domain is still needed before using this in a real product.

## Suggested next improvements

1. Add a neutral class and more diverse labeled examples.
2. Inspect misclassified test examples.
3. Evaluate separately on each source domain.
4. Compare with a contextual transformer model.
5. Add multilingual training data if Amharic support is required.

---
Built as a learning and portfolio project.