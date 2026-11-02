# B — Data Analysis Report

This report addresses the numbered analysis tasks using code-generated tables from the cleaned master data. Results are descriptive; they do not prove causal effects. All supplied data is synthetic and illustrative.

## B1 — Demand patterns

### B1.1 Volume by zone

Zone totals and shares are in `B1_zone_demand.csv`. Highest total-demand zones in this cleaned extract:
- **MERKATO**: 288,049 trips, 12.1% of cleaned observed trips, mean 40.9 trips/zone-hour across 7,050 rows.
- **BOLE**: 279,622 trips, 11.7% of cleaned observed trips, mean 39.5 trips/zone-hour across 7,075 rows.
- **MEGENAGNA**: 274,220 trips, 11.5% of cleaned observed trips, mean 38.8 trips/zone-hour across 7,063 rows.
- **KAZANCHIS**: 226,904 trips, 9.5% of cleaned observed trips, mean 32.1 trips/zone-hour across 7,069 rows.

Interpretation: observed totals combine demand intensity with how many hours a zone appears in the raw history. Use `zone_hours` and the gap report before ranking zones as if all had identical coverage.

### B1.2 Hour-of-day profile by zone type

Hourly profiles by zone are in `B2_hourly_profiles.csv` and `fig05_zone_profiles.png`. The zone labels are normalized; descriptive zone-type groupings are interpretive rather than official classifications. Peaks differ by zone, so a citywide average alone can hide important local patterns.

### B1.3 Weekday vs weekend

The weekend-to-weekday mean ratio for each zone is in `B3_weekend_ratio.csv`.
- Weekend-busier candidates: **BOLE** ratio 1.32.
- Weekend-busier candidates: **GERJI** ratio 1.08.
- Weekend-busier candidates: **KOLFE** ratio 1.08.
- Weekend-quieter candidates: **ARAT KILO** ratio 0.49.
- Weekend-quieter candidates: **PIASSA** ratio 0.49.
- Weekend-quieter candidates: **KAZANCHIS** ratio 0.51.

Ratios are mean trips per observed zone-hour; gaps and unequal operating history can affect comparisons.

### B1.4 Trend, January–October

Weekly city totals are in `B1_weekly_city_totals.csv`; first observed weekly total is 31,142 and last observed weekly total is 51,202. The full daily series and 7-day mean are in `fig03_demand_trend_with_holidays.png`. Trend and coverage both matter: November is a future period, so a model trained only on earlier levels may under- or over-extrapolate if demand is changing.

## B2 — Weather

### B2.1 Timezone check

Weather UTC/offset timestamps are converted to Addis Ababa local time (EAT, UTC+03:00). The code tested rain–demand correlation under offsets −5…+5 hours; see `B2_1_clock_shift_test.csv` and `fig06_weather_timezone_check.png`. The selected clock is based on timestamp semantics and format evidence, not just the highest correlation. The training table has weather measurements on approximately 84.1% of observed zone-hour rows after the join.

### B2.2 Rain effect by zone type

Rain comparisons are in `B2_rain_summary.csv` and `fig07_rain_effect.png`. The analysis compares average demand across rain classes and broad zone groupings; it is observational and can be confounded by hour, weekday, and zone. A more rigorous extension would match rainy hours to dry hours with the same zone, weekday, and hour.

### B2.3 Rain dose-response

Rain is binned into none, light (0–2 mm), moderate (2–10 mm), and heavy (>10 mm) classes. The code-generated means and counts are in `B2_rain_summary.csv`; inspect sample counts before interpreting heavy-rain changes. Response need not be proportional, especially in sparse heavy-rain bins.

## B3 — Events and calendar

### B3.1 Public holidays

Holiday dates and their observed daily totals versus same-weekday non-holiday baselines are in `B3_holiday_effects.csv` and `fig09_holiday_effects.png`. A holiday does not have to reduce demand in every zone; local travel and event activity can offset citywide patterns.

### B3.2 Football match event study

The event study figure is `fig08_event_study.png`. The implementation aligns demand around event starts and compares the event-window shape descriptively. Zone aliases and event coverage are imperfect, so sparse event windows are not strong causal estimates.

### B3.3 Event type ranking

A rough event-window comparison is saved in `B3_event_type_effects.csv`. It compares trips in matched event windows with same-zone weekday/hour observations outside nearby event dates. Event coverage and zone matching can be sparse; interpret ranking as exploratory, not causal.

### B3.4 Cancelled and unlisted events

The supplied calendar has 165 event rows, including 6 rows marked cancelled. Cancelled events are excluded from model features. Three high-trip zone-hours outside any detected event window are listed in `B3_unlisted_spikes.csv`; they are candidates for unlisted events, service disruptions, or data artifacts, and the data alone cannot identify the true explanation.

## B4 — Operations and data quality

### B4.1 Operational variables vs demand

Historical correlations are in `B4_operational_correlations.csv`. `active_drivers` and `avg_wait_min` are likely partly responses to demand and dispatch behavior, while fare may reflect trip mix and time. Correlation is not causation, and these train-only fields are excluded from forecast inputs because they are unavailable for future test hours.

### B4.2 Gaps and outages

Coverage by zone is in `B4_gaps_by_zone.csv`; `fig01_gaps_and_missingness.png` visualizes missingness and observed zone-hours. A missing zone-hour may be a true zero, random missing record, outage, or late zone launch. Without an explicit platform-status table, these categories cannot always be distinguished with confidence; the current pipeline does not fabricate target values for missing historical records.

### B4.3 Pay-period effect

The code-generated payday comparison is in `B4_pay_period_effect.csv`. It compares average demand near month-end/month-start (days 28–3) with other days. This is an exploratory, not fully detrended causal estimate; if the difference is small or inconsistent by zone, do not keep payday as a strong feature without further time-aware testing.

## Key takeaway

Ride demand has strong zone/hour/weekday structure. Weather and event tables provide useful operational context and are required model feature families, but their incremental predictive value should be judged by chronological ablation rather than assumed. The seasonal baseline is strong, so model improvements must be demonstrated against it.
