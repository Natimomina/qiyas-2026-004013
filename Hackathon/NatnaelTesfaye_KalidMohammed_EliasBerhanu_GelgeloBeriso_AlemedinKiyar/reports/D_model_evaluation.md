# D — Modeling & Evaluation

## D1 Baselines
80/20 held-out split, random_state=42.

| model         |     RMSE |      MAE |           R2 |   training_time_s |
|:--------------|---------:|---------:|-------------:|------------------:|
| Mean baseline | 1.3649   | 1.08643  | -0.000291039 |        0.00401473 |
| Ridge linear  | 0.860652 | 0.658691 |  0.602281    |        0.0191314  |

## D2 Model comparison
| model                |     RMSE |      MAE |           R2 |   training_time_s |
|:---------------------|---------:|---------:|-------------:|------------------:|
| Mean baseline        | 1.3649   | 1.08643  | -0.000291039 |        0.00401473 |
| Ridge linear         | 0.860652 | 0.658691 |  0.602281    |        0.0191314  |
| Random forest        | 0.540823 | 0.402639 |  0.842952    |        2.25551    |
| Extra trees          | 0.583382 | 0.43216  |  0.817262    |        1.23286    |
| HistGradientBoosting | 0.473845 | 0.350431 |  0.879442    |        1.621      |

**Winner:** tuned HistGradientBoosting.

## D3 Cross-validation
Final 5-fold RMSE = **0.488 ± 0.013 t/ha**. Runner-up Ridge = **0.892 ± 0.019 t/ha**.

## D4 Out-of-time
2024 RMSE = **0.506**, MAE = **0.368**, R² = **0.875**, versus random-split RMSE **0.473**.

## D5 Weather ablation
| feature_set     |     RMSE |      MAE |       R2 |
|:----------------|---------:|---------:|---------:|
| with weather    | 0.47296  | 0.349132 | 0.879892 |
| without weather | 0.517617 | 0.378727 | 0.85614  |

**Interpretation:** Adding weather changes RMSE by **0.045 t/ha** (positive means weather improves prediction).

## D6 Tuning
Three candidate parameter sets were tested on the fixed training/validation split.

|   trial |     RMSE |   fit_time_s |
|--------:|---------:|-------------:|
|       1 | 0.47296  |     2.29968  |
|       2 | 0.473845 |     1.72609  |
|       3 | 0.591661 |     0.873997 |

Best parameters: `{"max_iter": 160, "learning_rate": 0.1, "max_leaf_nodes": 15, "min_samples_leaf": 20, "l2_regularization": 1.0}`.

## D7 Error analysis
Crop and region error tables are in `error_by_crop.csv` and `error_by_region.csv`; continuous-error tables cover altitude and temperature anomaly. The 10 largest validation errors are in `top10_validation_errors.csv`.

**Hypothesis:** the hardest observations combine unusual climate, noisy management inputs, or difficult region/crop combinations.

## D8 Response to findings
The crop × temperature-band interaction test is in `D8_response.json`; it is compared against the fixed validation score before the change.

## D9 Plain-language metric
RMSE is **0.473 t/ha**, about **17.1%** of mean yield (2.76 t/ha). At the average cleaned price (4,624 birr/quintal), an RMSE-sized error is roughly **21,870 birr/ha**.
