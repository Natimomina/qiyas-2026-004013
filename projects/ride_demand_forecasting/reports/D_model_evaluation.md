# D — Modeling & Evaluation Report

## D1. Baselines

Chronological validation holds out **18–31 October 2025** (the final 14 calendar days with training history). The target is trips per zone-hour. Scores are computed only on this held-out training window; the November test file is not used for evaluation.

| Model | RMSE | MAE | R² |
|---|---:|---:|---:|
| Mean baseline | 29.63 | 20.98 | -0.032 |
| Seasonal naive (zone × weekday × hour) | 15.52 | 7.58 | 0.717 |

The seasonal-naive baseline is strong because demand has recurring zone/hour/weekday structure. It is a meaningful benchmark; a more complex model must beat it to justify complexity.

## D2. Model comparison

See `D_model_comparison.csv` and `fig10_model_comparison.png` for all models and training times. The Random Forest achieved the lowest RMSE of the tested ML families on this split (**14.97 RMSE, 7.33 MAE, R² 0.737**), below the seasonal baseline on both RMSE and MAE. Ridge and HistGradientBoosting did not outperform the seasonal baseline. The model comparison uses a runtime-conscious sample for tree model fitting; the same chronological validation rows are used for comparison. The tuned final configuration performs better than the seasonal baseline on both RMSE and MAE on this split, but the margin should still be validated over future windows.

## D3. Rolling-origin validation

`D_rolling_origin.csv` reports four successive 14-day windows, with training restricted to rows before each validation window. Random Forest is close to the seasonal baseline overall; the model wins in some folds and loses in others. The October 4–17 fold is harder for Random Forest, suggesting that recent demand conditions can change and that a seasonal baseline remains competitive. The final held-out window RF RMSE is approximately 14.91 in the rolling-origin run. RF outperforms the seasonal baseline in all four folds, although the improvement is very small in the 4–17 October fold; the baseline remains useful because its MAE is competitive and it is simpler.

## D4. Feature availability and leakage audit

See `D4_feature_availability_audit.csv`. Included predictors are zone/calendar/trend, weather values available for the forecast period, and event features from the supplied event calendar. Excluded predictors are `avg_fare_birr`, `avg_wait_min`, and `active_drivers`: they appear only in the training history and are not known for future zone-hours. The target `trips` is never used as a predictor. No score is reported on the hidden November target.

## D5. Ablation

See `D_ablation.csv`. On the held-out window, calendar + zone + trend was approximately **15.39 RMSE / 7.67 MAE**; adding weather alone was approximately **14.99 / 7.30**; adding events alone was approximately **15.04 / 7.47**; and adding both was approximately **14.91 / 7.26**. Weather and event features improve the calendar-only RMSE on this split, and the combined weather+events configuration is marginally best. Adding weather to events changes the score only slightly, so the incremental contribution of weather on top of event features is small. These are runtime-conscious RF ablation results and should be interpreted as a useful first pass rather than exhaustive tuning.

## D6. Tuning

A small, reproducible 4-trial search is recorded in `D6_tuning.csv`, using the same chronological 14-day validation window and 22,000 training rows sampled only from the pre-validation period. The tested search space varied tree count (16–32), maximum depth (10–14), and minimum leaf size (3–5). The best of these trials used **24 trees, max depth 14, minimum leaf size 5**, reaching **14.91 RMSE / 7.26 MAE** on the validation sample. The final model uses this configuration. This is a compact time-aware search, not an exhaustive global optimization.

## D7. Error analysis

Generated outputs: `D_error_by_zone.csv`, `D_error_by_hour.csv`, `D_largest_errors.csv`, and `fig11_forecast_vs_actual.png`. The largest-error rows are listed in code-generated form. Hypotheses include unusual demand spikes not represented in the event calendar, zone-specific changes, weather forecast uncertainty, and demand drift. These are hypotheses for investigation, not established causes.

## D8. Response to findings

The strong seasonal baseline and modest RF improvement suggest keeping the baseline in the evaluation suite, avoiding overclaiming model superiority, and focusing future work on better event matching, gap/outage treatment, and temporal feature design. The ablation results support a measurable improvement from adding weather and event features to the calendar-only feature set, although the incremental gain from adding weather on top of event features is small.

## D9. Plain-language interpretation

On the final 14-day validation window, tuned RF RMSE of about **14.91 trips per zone-hour** means larger misses are penalized and the typical error scale is roughly fifteen trips in one zone during one hour. MAE is about **7.26 trips per zone-hour**. With the challenge's planning assumption of about 1.3 trips per active driver-hour, the MAE scale corresponds to roughly **6 drivers** worth of hourly capacity (7.26 ÷ 1.3), although actual staffing needs depend on trip duration, shift overlap, and spatial availability. These are synthetic-data validation results, not guaranteed live performance.

## Submission QA

`submission/team_ride_demand_submission.csv` has 4,032 rows, the required columns `row_id` and `predicted_trips`, template row order, no missing predictions, and no negative predictions. Predictions are generated for every provided test row.
