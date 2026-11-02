# A — Cleaning & Integration Report

## A1. Cleaning log

The detailed, code-generated log is `A1_cleaning_log.csv`. It records source file, column, issue type, affected row count, applied fix, and rationale. The pipeline covers: mixed timestamp formats; zone aliases/case/whitespace; negative trip targets; invalid operational values; duplicate weather timestamps; impossible weather ranges; event type aliases; missing or reversed event ends; and invalid event starts.

Raw source files in `data/raw/` are preserved. Cleaning writes only to `data/processed/` and `reports/`.

## A2. Time and key standardization

- Trip timestamps are local pickup-hour labels in Addis Ababa time. Naive timestamps are interpreted as EAT; explicit offsets are converted to EAT.
- Weather ISO timestamps ending in `Z` are UTC and are converted to `Africa/Addis_Ababa` (UTC+03:00). This matters because joining the raw UTC clock directly to local pickup hours would shift weather context by three hours. The provided weather table also contains a small number of non-ISO naive timestamps; those are interpreted as local EAT and flagged in the cleaning logic.
- Event timestamps are local event times, written in mixed formats. Where one event endpoint is explicit and the other is an ambiguous slash date, the pair is used to resolve a plausible nonnegative interval; otherwise day-first parsing is used and malformed/reversed intervals are logged.
- Zone spellings are normalized to the same 12 canonical labels across trip, test, and event data. See `A2_zone_normalization.csv`.

Clock evidence: the code compares the rain–demand correlation under offsets from −5 to +5 hours in `B2_1_clock_shift_test.csv` and plots the result in `fig06_weather_timezone_check.png`. The primary conversion decision comes from timestamp semantics (`Z` means UTC), not from choosing whichever shift gives the largest correlation.

## A3. Join map and cardinality

```text
Trip history / test zone-hour (left table; preserve every requested row)
       | normalized local pickup_hour
       | LEFT JOIN, many-to-one
       v
Weather hourly table (UTC/offset normalized to EAT; duplicate hours aggregated)

Trip zone-hour
       | zone + event interval, including citywide events
       | interval-derived flags; 2h before start through 2h after end
       v
Event calendar (cancelled events excluded from model features)
       v
Master zone-hour table: calendar + weather + event features
```

The weather table is aggregated to one row per local hour before joining. This prevents a duplicate weather key from multiplying trip rows. The trip table is the left table because a missing weather row should not erase a required prediction row. Events are not joined by exact timestamp: each event is expanded conceptually into an affected zone/time interval and encoded as flags and timing features.

## A4. Join audit

See `A_join_audit.json`, `A5_join_proof_examples.csv`, and `A7_integrity_checks.csv` for the generated row counts, weather match rate, duplicate-key checks, normalized zone count, and cancellation counts. The integrity checks confirm that processed test row count and IDs are preserved and weather keys are unique. Missing weather values are retained as missing, marked by `weather_missing`, and imputed by the model's preprocessing pipeline rather than deleting the zone-hour.

## A5. Join proof

Use `master_train.csv` to inspect any concrete zone-hour. For each proof row, `pickup_hour` is already in EAT; `rain_mm`/`temp_c` show the matched weather row; `event_in_window`, event-type flags, and `event_count` show the event interval features. The code-generated master table is the source of truth for this proof; do not manually edit values in a report.

## A6. Feature engineering table

| Feature family | Example features | Formula / source | Known at forecast time? |
|---|---|---|---|
| Calendar | `hour`, `day_of_week`, `is_weekend`, `month`, `day_of_year` | Parsed `pickup_hour` | Yes |
| Cyclic calendar | `hour_sin`, `hour_cos`, `dow_sin`, `dow_cos` | Sine/cosine transforms of hour and weekday | Yes |
| Trend | `trend_days`, `week_of_year` | Elapsed days and calendar week | Yes |
| Weather | `temp_c`, `rain_mm`, `humidity_pct`, `wind_kmh` | Hour-aligned weather table | Yes for supplied forecast period; weather forecast has uncertainty |
| Weather quality | `weather_missing`, `is_forecast`, `rain_class` | Missingness, forecast marker, rainfall bins | Yes |
| Events | `event_count`, `event_in_window`, `event_football_match`, `event_public_holiday`, etc. | Non-cancelled event interval/zone matching | Yes, given the provided calendar |
| Event timing | `event_hours_to_start`, `event_hours_since_end` | Distance to nearest relevant event interval | Yes |
| Operational columns | `avg_fare_birr`, `avg_wait_min`, `active_drivers` | Train-only operational history | **No — excluded from model inputs** |
| Target | `trips` | Observed trip count | **No — target only; absent from test** |

## A7. Integrity checks

Run `notebooks/01_cleaning_and_integration.ipynb` or `python src/pipeline.py` to regenerate the printed PASS/FAIL checks. The latest run is stored in `A7_integrity_checks.csv`. The checks cover unique zone-hour keys, test row preservation, unique IDs, 12 normalized zones, no negative target values, exclusion of train-only operational features, and unique weather keys.

## A8. Master tables and dictionary

- `data/processed/master_train.csv`: cleaned/engineered training observations plus target.
- `data/processed/master_test.csv`: the same forecast-time feature columns without target.
- `data/processed/data_dictionary_master.csv`: column types, source, description, and derivation.

The model's fitted preprocessing learns imputations/encodings from the training fold only. Test rows are transformed with that fitted preprocessing; the hidden test target is never read or scored.
