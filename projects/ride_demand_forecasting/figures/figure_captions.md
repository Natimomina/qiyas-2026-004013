# Figure captions

**fig01_gaps_and_missingness.png** — Raw trip columns contain missing values, and coverage differs by zone; inspect the gap report before interpreting zone totals.

**fig02_before_after_cleaning.png** — Cleaning removes invalid target values and aligns weather values; distributions should be interpreted alongside the cleaning log.

**fig03_demand_trend_with_holidays.png** — Daily city-wide demand and its seven-day moving average show the level and trend the forecasting model must generalize to.

**fig04_hour_by_weekday_heatmap.png** — Hour-by-weekday profiles expose recurring weekly and intraday patterns that support calendar features.

**fig05_zone_profiles.png** — Zone-level weekday/weekend curves reveal that demand shape differs across locations.

**fig06_weather_timezone_check.png** — The rain–demand correlation changes under shifted joins; use the timestamp evidence and explicit UTC-to-EAT conversion rather than choosing a shift solely by correlation.

**fig07_rain_effect.png** — Rain-class ratios compare demand during rainy hours with dry-hour baselines; differences are descriptive, not causal proof.

**fig08_event_study.png** — Event-start curves summarize available demand around event times; sparse matching should be reported as a limitation rather than overinterpreted.

**fig09_holiday_effects.png** — The holiday index compares observed daily demand with non-holiday days; values above one indicate higher observed volume.

**fig10_model_comparison.png** — Chronological validation RMSE compares simple baselines and candidate models on the same later time window.

**fig11_forecast_vs_actual.png** — Actual and predicted series on held-out later hours show how well the selected model tracks demand in example zones.

**fig12_feature_importance.png** — Permutation importance estimates how much error increases when a feature is shuffled; weather and event features are included in the candidate set.
