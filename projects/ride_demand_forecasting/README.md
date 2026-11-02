# Addis Ride Demand Forecasting

A reproducible end-to-end forecasting project for the synthetic Qiyas ride-demand challenge. It integrates trip history, hourly weather, and city events; generates analysis and visualizations; compares forecasting models with chronological validation; produces the 4,032-row submission; and includes a modern Streamlit operations demo.

> **Data note:** The challenge instructions state that all supplied data is synthetic and illustrative. Results are not real-world performance claims.

## Quick start

Python 3.10+ is recommended. From the project root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Run the notebooks in this order:

1. `notebooks/01_cleaning_and_integration.ipynb` — cleaning, timestamp normalization, joins, audit, master tables.
2. `notebooks/02_analysis_report.ipynb` — demand, weather, event, and operational analysis.
3. `notebooks/03_visualizations.ipynb` — the 12 required PNG figures and captions.
4. `notebooks/04_modeling_and_evaluation.ipynb` — chronological validation, model comparison, rolling-origin checks, ablation, error analysis, and submission generation.

The notebooks use the reusable implementation in `src/pipeline.py` and `src/visualizations.py`. You can also run the complete pipeline from a terminal:

```bash
python src/pipeline.py
python src/visualizations.py
```

Start the interactive demo locally:

```bash
streamlit run app/app.py
```

The demo supports dates **1–14 November 2025** and lets an operations user select only a zone and date. It automatically looks up the supplied weather forecast and event calendar, then shows hourly trips, peak demand, estimated drivers, and estimated gross fares. Hosting is not configured in this package; it is ready to run locally and can be deployed to Streamlit Community Cloud or Hugging Face Spaces.

## Main outputs

- `submission/team_ride_demand_submission.csv` — exactly `row_id,predicted_trips`, 4,032 rows in template order.
- `data/processed/master_train.csv`, `master_test.csv`, `data_dictionary_master.csv`, `weather_hourly_clean.csv`, `events_calendar_clean.csv` — cleaned and engineered tables.
- `reports/A_cleaning_and_integration.md`, `reports/B_analysis_report.md`, `reports/D_model_evaluation.md` — written deliverables.
- `figures/fig01_...png` through `fig12_...png` plus `figures/figure_captions.md` — visualization pack.
- `models/final_model.joblib` — fitted model bundle and feature list.
- `app/app.py` — modern dark editorial Streamlit interface.

## Model and validation summary

The validation split is chronological: the final 14 days of the training period (18–31 October 2025) are held out; no score is computed against the hidden test answers. On this split, the Random Forest achieved approximately **14.97 RMSE** and **7.33 MAE trips per zone-hour**. The seasonal-naive baseline achieved **15.52 RMSE** and **7.58 MAE**. The RF outperforms the seasonal baseline on this holdout, but its margin should still be checked across rolling-origin windows. A compact four-trial time-aware parameter search is recorded in `reports/D6_tuning.csv`; the selected final configuration uses 24 trees, depth 14, and minimum leaf size 5. Four rolling-origin 14-day evaluations are included in `reports/D_rolling_origin.csv`.

The final model includes calendar/zone, weather, and event-derived features as required. It excludes `avg_fare_birr`, `avg_wait_min`, and `active_drivers` from model inputs because they are only available in historical training rows and would be unavailable for future forecast hours. Fare history is used only by the demo to estimate gross fares.

## Time and join policy

- Naive trip and event timestamps are interpreted as Addis Ababa local time (EAT, UTC+03:00).
- Weather timestamps with `Z` or an explicit UTC offset are converted to `Africa/Addis_Ababa`; naive weather timestamps are interpreted as local.
- Weather is aggregated to one row per local hour before a **left, many-to-one** join to preserve the trip rows.
- Events are treated as intervals, not point timestamps. Non-cancelled event windows extend from 2 hours before start to 2 hours after end. See the cleaning report for caveats and audit outputs.

## Important limitations

- The model's improvement over the seasonal baseline is small. The ablation results show that weather/event additions are not consistently helpful on the held-out period, even though those feature families are included to satisfy the challenge requirements. Report that honestly.
- The current tuning is a transparent, runtime-conscious baseline, not an exhaustive hyperparameter search. Further tuning should use time-ordered folds only.
- The application is a local demo prototype, not a production dispatch system.
