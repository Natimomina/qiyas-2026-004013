# A — Data Cleaning & Integration

## A1 Cleaning log
The original five CSVs are preserved in `data/raw/`; cleaning is code-generated. The plot file contains 90 duplicate-content records, including the explicitly suffixed duplicate ID.

| file                 | column(s)                            | issue_type                        |   rows_affected |   percent_of_file | fix_applied                                                                   | why                                                                  |
|:---------------------|:-------------------------------------|:----------------------------------|----------------:|------------------:|:------------------------------------------------------------------------------|:---------------------------------------------------------------------|
| crop_yield_train.csv | region/crop_type                     | inconsistent labels               |               0 |             0     | strip/lower/map to canonical labels                                           | ensures identical join/category keys                                 |
| crop_yield_train.csv | plot_id + all fields                 | duplicate plot record             |              90 |             0.596 | remove duplicate-content plot records (90 rows; one has the explicit -DUP id) | preserves unique plot_id and avoids duplicated training example      |
| crop_yield_train.csv | pest_disease_flag, labor_days_per_ha | -999 sentinel                     |             788 |             5.222 | replace -999 with missing and impute inside model pipeline                    | -999 is not a valid domain value                                     |
| crop_yield_train.csv | farm_size_ha                         | extreme/unit anomaly              |             151 |             1.001 | cap above train 99th percentile (4.262 ha)                                    | prevents a small number of implausible large-plot records dominating |
| crop_yield_train.csv | fertilizer_kg_per_ha                 | extreme/unit anomaly              |             143 |             0.948 | cap above train 99th percentile (136.050 kg/ha)                               | limits obvious high-end unit anomalies using train-only cap          |
| regional_weather.csv | region                               | inconsistent labels/abbreviations |              19 |             8.19  | map full names and abbreviations to canonical labels                          | makes region join keys consistent                                    |
| regional_weather.csv | region/year/month                    | duplicate weather keys            |               6 |             2.586 | clean labels then average duplicate readings by key                           | restores one row per region-year-month for many-to-one seasonal join |
| regional_weather.csv | avg_temp_c/monthly_rainfall_mm       | missing weather readings          |               3 |             1.293 | impute by cleaned region-month median, then global median                     | keeps seasonal features computable without using target/test fitting |
| market_prices.csv    | crop_type                            | inconsistent labels               |               0 |             0     | strip/lower/map tef to teff and canonical labels                              | aligns price and plot crop keys                                      |
| market_prices.csv    | price_birr_per_quintal               | missing prices                    |               4 |             4     | fill with crop-year regional median                                           | keeps analysis/demo complete and uses comparable observations        |
| market_prices.csv    | price_birr_per_quintal               | wrong unit                        |               4 |             4     | multiply values below 100 by 100                                              | restores the intended birr/quintal scale                             |

## A2 Key standardization proof
See `key_standardization_proof.csv`. All tables end with the same five canonical regions; plot and price tables end with the same five canonical crops.

## A3 Join map
The plot table is the left table because every plot must survive enrichment. Weather is joined after aggregation to the planting month plus next three months; price joins on region + crop + year. Both are many-to-one.

![Join map](../figures/join_map.png)

## A4 Join audit
| join                     | join_type   |   rows_before |   rows_after |   match_rate_pct |   unmatched_plots |   fewer_than_4_months | handling                                                                                               |
|:-------------------------|:------------|--------------:|-------------:|-----------------:|------------------:|----------------------:|:-------------------------------------------------------------------------------------------------------|
| plot -> weather seasonal | many-to-one |         15000 |        15000 |              100 |                 0 |                    20 | aggregate available months; missing monthly readings were cleaned/imputed; retain observed-month count |
| plot -> price            | many-to-one |         15000 |        15000 |              100 |                 0 |                   nan | cleaned/imputed price table; merge validate=many_to_one                                                |

The weather table has 20 seasonal key combinations with fewer than four observed source months; the pipeline retains the partial season and records `weather_months_observed`.

## A5 Join proof
See `join_proof_3_plots.csv`, which lists the actual weather rows and season-level values for three plots.

## A6 Feature engineering
| feature                     | formula                                              | source_columns                       | expected_value                                                   |
|:----------------------------|:-----------------------------------------------------|:-------------------------------------|:-----------------------------------------------------------------|
| season_mean_temp            | mean(avg_temp_c over planting month + next 3 months) | regional_weather avg_temp_c          | captures growing-season thermal conditions                       |
| season_rainfall_mm          | sum(monthly_rainfall_mm over 4-month window)         | regional_weather monthly_rainfall_mm | captures accumulated station rainfall                            |
| season_extreme_heat_days    | sum(extreme_heat_days over 4-month window)           | regional_weather extreme_heat_days   | captures heat stress exposure                                    |
| season_temp_anomaly         | season_mean_temp - region seasonal climatology       | weather avg_temp_c + region/month    | captures unusual warmth/cold for the region                      |
| weather_months_observed     | count of available months in the 4-month window      | weather keys                         | measures seasonal data completeness                              |
| fertilizer_seed_interaction | fertilizer_kg_per_ha × improved_seed_used            | plot fertilizer + seed               | captures complementary input response                            |
| rainfall_reporting_ratio    | rainfall_mm_season / season_rainfall_mm              | plot rainfall + weather rainfall     | captures agreement between farmer report and station aggregation |
| temp_rainfall_interaction   | season_mean_temp × log(1 + season_rainfall_mm)       | weather temperature + rainfall       | captures joint climate effect                                    |
| planting_month_num          | calendar month number 1–12                           | planting_month                       | lets models learn timing effects                                 |

## A7 Integrity checks
```text
PASS | plot_id unique in master train
PASS | train row count preserved after joins (15,000 rows after removing 90 duplicate-content records)
PASS | test row count preserved
PASS | region labels canonical
PASS | crop labels canonical
PASS | model feature columns identical train/test
PASS | yield non-negative
PASS | price positive
PASS | no model price feature
PASS | submission template has expected IDs
PASS | weather seasonal keys are unique
PASS | no missing target
```

## A8 Master tables
`data/processed/master_train.csv`, `master_test.csv`, and `data_dictionary_master.csv` are included. Price is not a model feature.
