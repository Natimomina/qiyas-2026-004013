# B — Data Analysis Report

## B1.1 Revenue per hectare
| crop_type   |   mean_yield_t_ha |   mean_price_birr_q |   mean_revenue_birr_ha |
|:------------|------------------:|--------------------:|-----------------------:|
| teff        |           2.00202 |             7691    |               153289   |
| wheat       |           2.80116 |             4845.98 |               135438   |
| maize       |           3.90039 |             2930.97 |               114356   |
| barley      |           2.4673  |             4479.66 |               110218   |
| sorghum     |           2.61137 |             3180.16 |                83275.8 |

**Interpretation:** teff has the highest mean revenue (153,289 birr/ha). The highest-yield crop is maize; the two leaders are different.

## B1.2 Price trend
| crop_type   |   2021 |   2022 |   2023 |   2024 |   absolute_change |   pct_change |
|:------------|-------:|-------:|-------:|-------:|------------------:|-------------:|
| barley      | 3946.8 | 4189.2 | 4769.6 | 4977.8 |            1031   |      26.1224 |
| maize       | 2602.2 | 2850.2 | 3055.5 | 3233.2 |             631   |      24.2487 |
| sorghum     | 2688.8 | 3068.2 | 3475.6 | 3492.4 |             803.6 |      29.8869 |
| teff        | 6885   | 7398.2 | 8033   | 8575.3 |            1690.3 |      24.5505 |
| wheat       | 4305   | 4715.2 | 4783   | 5557.4 |            1252.4 |      29.0918 |

**Interpretation:** sorghum has the fastest percentage growth (29.9%).

## B2.1 Yield by region
| region   |    mean |   median |      std |   count |
|:---------|--------:|---------:|---------:|--------:|
| Amhara   | 3.12751 |  3.01961 | 1.23121  |    2962 |
| Oromia   | 3.06996 |  2.89074 | 1.29002  |    2957 |
| SNNPR    | 3.03866 |  2.7398  | 1.47102  |    2962 |
| Somali   | 1.46549 |  1.29428 | 0.771337 |    3049 |
| Tigray   | 3.12842 |  2.9308  | 1.30572  |    3070 |

**Interpretation:** Tigray has the highest mean; SNNPR is most variable.

## B2.2 Yield by crop
| crop_type   |    mean |   median |      std |   count |
|:------------|--------:|---------:|---------:|--------:|
| barley      | 2.4673  |  2.37586 | 1.15682  |    2918 |
| maize       | 3.90039 |  3.77259 | 1.58292  |    3036 |
| sorghum     | 2.61137 |  2.51348 | 0.974867 |    2991 |
| teff        | 2.00202 |  2.00104 | 0.986924 |    3001 |
| wheat       | 2.80116 |  2.69275 | 1.40603  |    3054 |

**Interpretation:** maize has the highest average yield.

## B2.3 Region × crop
| region   |   barley |   maize |   sorghum |   teff |   wheat |
|:---------|---------:|--------:|----------:|-------:|--------:|
| Amhara   |     3.19 |    3.83 |      2.50 |   2.47 |    3.60 |
| Oromia   |     2.68 |    4.44 |      2.96 |   2.29 |    3.12 |
| SNNPR    |     2.29 |    4.79 |      3.10 |   2.10 |    2.67 |
| Somali   |     1.12 |    2.32 |      1.79 |   0.83 |    1.28 |
| Tigray   |     3.01 |    4.07 |      2.71 |   2.33 |    3.45 |

**Interpretation:** Best = ('SNNPR', 'maize') (4.79 t/ha); worst = ('Somali', 'teff') (0.83 t/ha). Crop suitability and local climate are plausible reasons.

## B2.4 Improved seed
| crop_type   |   gap_t_ha |   pct_lift |
|:------------|-----------:|-----------:|
| barley      |   0.417752 |    18.1028 |
| maize       |   0.781642 |    21.6584 |
| sorghum     |   0.450448 |    18.4542 |
| teff        |   0.420897 |    22.8379 |
| wheat       |   0.535673 |    20.6322 |

**Interpretation:** teff has the largest percentage lift (22.8%).

## B2.5 Pest/disease
| crop_type   |   gap_t_ha |   pct_lift |
|:------------|-----------:|-----------:|
| barley      |  -0.70325  |   -26.8081 |
| maize       |  -1.21236  |   -28.9906 |
| sorghum     |  -0.746663 |   -26.9334 |
| teff        |  -0.558691 |   -26.2546 |
| wheat       |  -0.785288 |   -26.366  |

**Interpretation:** maize has the largest absolute penalty; maize has the largest relative penalty.

## B3.1 Fertilizer response
See `B3_1_fertilizer_bands.csv` and the crop-level table.

## B3.2 Altitude
See `B3_2_altitude_by_crop.csv`; cells with fewer than 30 plots should not be trusted strongly.

## B3.3 Planting month
See `B3_3_planting_month.csv`; timing differs by crop and is retained in the model.

## B3.4 Distance to market
Correlation with yield = **0.006**. See the binned comparison in `B3_4_distance_bands.csv`.

## B4.1 Yield trend
See `B4_1_year_region.csv`. Year effects are interpreted relative to the much larger region/crop spread.

## B4.2 Weather anomalies
| region   |   survey_year |   season_mean_temp |   region_avg |    anomaly |
|:---------|--------------:|-------------------:|-------------:|-----------:|
| Amhara   |          2021 |            16.7349 |      16.7843 | -0.0493636 |
| Amhara   |          2022 |            18.312  |      16.7843 |  1.52771   |
| Amhara   |          2023 |            15.5065 |      16.7843 | -1.27771   |
| Amhara   |          2024 |            16.5836 |      16.7843 | -0.200641  |
| Oromia   |          2021 |            19.1284 |      18.8599 |  0.268488  |
| Oromia   |          2022 |            19.7126 |      18.8599 |  0.8527    |
| Oromia   |          2023 |            18.5017 |      18.8599 | -0.358194  |
| Oromia   |          2024 |            18.0969 |      18.8599 | -0.762994  |
| SNNPR    |          2021 |            21.3911 |      20.1477 |  1.2434    |
| SNNPR    |          2022 |            19.7136 |      20.1477 | -0.434161  |
| SNNPR    |          2023 |            19.6868 |      20.1477 | -0.460906  |
| SNNPR    |          2024 |            19.7994 |      20.1477 | -0.348331  |
| Somali   |          2021 |            30.1451 |      28.3964 |  1.74868   |
| Somali   |          2022 |            25.9188 |      28.3964 | -2.47762   |
| Somali   |          2023 |            28.7957 |      28.3964 |  0.399289  |
| Somali   |          2024 |            28.7261 |      28.3964 |  0.329643  |
| Tigray   |          2021 |            17.5976 |      17.7364 | -0.138825  |
| Tigray   |          2022 |            16.3421 |      17.7364 | -1.39436   |
| Tigray   |          2023 |            16.7054 |      17.7364 | -1.03105   |
| Tigray   |          2024 |            20.3006 |      17.7364 |  2.56423   |

**Interpretation:** Most unusual = Tigray 2024, anomaly 2.56 °C.

## B4.3 Rainfall comparison
Correlation = **0.007**; mean absolute difference = **501.2 mm**. Plot-reported mean = **856.3 mm**, station-season mean = **371.8 mm**. The measures differ because they represent different spatial and timing scales.
