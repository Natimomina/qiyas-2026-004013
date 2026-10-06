# Qiyas Hackathon Ethiopian Smallholder Crop-Yield Challenge

**Title:** Crop Yield Forecasting
**Members:** 
- Natnael Tesfaye (qiyas-2026-004013) 
- Kalid Mohammed (qiyas-2026-006697) 
- Elias Berhanu (qiyas-2026-002030) 
- Gelgelo Beriso (qiyas-2026-000133) 
- Alemedin Kiyar (qiyas-2026-006942)

## Summary
A reproducible regression workflow for Ethiopian smallholder crop-yield forecasting. The final model uses plot-level agronomic inputs plus growing-season weather features; market price is excluded from yield modeling and used for revenue analysis/demo.

## Validation
- RMSE: **0.473 t/ha**
- MAE: **0.349 t/ha**
- R²: **0.880**
- 5-fold RMSE: **0.488 ± 0.013 t/ha**
- 2024 out-of-time RMSE: **0.506 t/ha**

The hidden leaderboard score is not known until official scoring.

## Setup
```bash
pip install -r requirements.txt
```
Demo:
```bash
pip install -r app/requirements.txt
python app/app.py
```

## Notebook order
1. `notebooks/01_cleaning_and_integration.ipynb` — A
2. `notebooks/02_analysis_report.ipynb` — B
3. `notebooks/03_visualizations.ipynb` — C
4. `notebooks/04_modeling_and_evaluation.ipynb` — D

## Deliverables
A: `reports/A_cleaning_and_integration.md` + cleaning/join/feature/check files + `data/processed/`.
B: `reports/B_analysis_report.md`.
C: exact `fig01`–`fig12` PNGs + `figure_captions.md`.
D: `reports/D_model_evaluation.md`, model/tuning/CV/ablation/error files, `models/final_model.joblib`.
E: `app/app.py` + bundled weather/price assets.
F: `presentation/team_qiyas_crop_yield_slides.pptx`.
G: README + pinned requirements + valid submission.

## Submission
`submission/team_qiyas_crop_yield_submission.csv` contains exactly `plot_id` and `predicted_yield_tons_per_ha`, 3,750 rows, original order, unique IDs and numeric predictions.

## Hygiene
Weather-derived features are included in the final model; price is not. Raw files are unchanged. Cleaning and model preprocessing statistics are derived from training data. Random seed is 42.


## Transparent notebook implementation

The original submission archive contained four placeholder notebooks that only linked to the reports. To make the project genuinely reproducible and studyable, those notebooks have been replaced in this archive with full executable implementations.

Run them in this order:

1. `notebooks/01_cleaning_and_integration.ipynb`
2. `notebooks/02_analysis_report.ipynb`
3. `notebooks/03_visualizations.ipynb`
4. `notebooks/04_modeling_and_evaluation.ipynb`

The notebooks expose the cleaning, joins, feature engineering, analysis, visualization, modeling, cross-validation, weather ablation, tuning, error analysis, and submission-generation code.

**Important:** because the original archive did not contain the original generator scripts, these are transparent reconstructions of the implemented methodology from the supplied raw data, packaged reports, saved model, and generated outputs. They are not claimed to be byte-for-byte recovery of an omitted source script.

### Reproducing locally

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

Then run the notebooks in the order above. Notebook 04 creates a transparent model bundle and a transparent submission file in addition to preserving the original packaged submission.
