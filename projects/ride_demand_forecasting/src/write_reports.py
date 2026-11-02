from pathlib import Path
import pandas as pd, numpy as np, json
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'reports'; P=ROOT/'data/processed'; F=ROOT/'figures'
tr=pd.read_csv(P/'master_train.csv',parse_dates=['pickup_hour']).dropna(subset=['trips']); ev=pd.read_csv(R/'B3_cleaned_events.csv'); ev['start']=pd.to_datetime(ev.start,errors='coerce'); ev['end']=pd.to_datetime(ev.end,errors='coerce')
tr['date']=tr.pickup_hour.dt.floor('D'); tr['hour']=tr.pickup_hour.dt.hour; tr['dow']=tr.pickup_hour.dt.dayofweek; tr['day_type']=np.where(tr.dow>=5,'weekend','weekday')
# helpers
zone=tr.groupby('zone').agg(total=('trips','sum'),mean=('trips','mean'),n=('trips','size')).sort_values('total',ascending=False)
weekly=tr.set_index('pickup_hour').trips.resample('W').sum().dropna()
ratio=tr.groupby(['zone','day_type']).trips.mean().unstack(); ratio['ratio']=ratio.weekend/ratio.weekday
rain=tr.groupby('rain_class',observed=False).trips.agg(['mean','count']) if 'rain_class' in tr else pd.DataFrame()
clock=pd.read_csv(R/'B2_1_clock_shift_test.csv')
ops=pd.read_csv(R/'B4_operational_correlations.csv',index_col=0)
# event zone matches by normalized zone exact or citywide
valid_events=ev[(~ev.is_cancelled.astype(str).str.lower().isin(['true','1'])) & ev.start.notna() & ev.end.notna()]
# holiday comparisons
hol=[]
for _,e in valid_events[valid_events.event_type.eq('public_holiday')].iterrows():
 day=e.start.floor('D'); obs=tr.loc[tr.date.eq(day),'trips'].sum(); baseline=tr.loc[(tr.date.dt.dayofweek==day.dayofweek)&(~tr.date.between(day-pd.Timedelta(days=3),day+pd.Timedelta(days=3)))].groupby('date').trips.sum().mean(); hol.append((e.event_name,day.date(),obs,baseline,obs/baseline if baseline else np.nan))
# event type simple uplift in matched zone(s)
eff=[]
for typ,grp in valid_events.groupby('event_type'):
 in_vals=[]; out_vals=[]
 for _,e in grp.iterrows():
  z=str(e.zone_norm).upper(); city=any(x in z.lower() for x in ['citywide','city-wide','all zones','all'])
  zz=tr if city else tr[tr.zone.eq(z)]
  if zz.empty: continue
  win=zz[(zz.pickup_hour>=e.start-pd.Timedelta(hours=2))&(zz.pickup_hour<=e.end+pd.Timedelta(hours=2))]
  if len(win): in_vals.extend(win.trips.tolist())
  base=zz[(zz.pickup_hour.dt.dayofweek==e.start.dayofweek)&(zz.pickup_hour.dt.hour.between(e.start.hour-2,e.end.hour+2))&(~zz.date.between(e.start.floor('D')-pd.Timedelta(days=3),e.end.floor('D')+pd.Timedelta(days=3)))]
  if len(base): out_vals.extend(base.trips.tolist())
 if in_vals and out_vals: eff.append((typ,len(in_vals),np.mean(in_vals),np.mean(out_vals),np.mean(in_vals)/np.mean(out_vals)))
# biggest zone-hour observations outside event flags
sp=tr[tr.event_in_window.fillna(0).eq(0)].nlargest(3,'trips')[['zone','pickup_hour','trips','rain_mm','temp_c']]
# B report
lines=['# B — Data Analysis Report','', 'This report addresses the numbered analysis tasks using code-generated tables from the cleaned master data. Results are descriptive; they do not prove causal effects. All supplied data is synthetic and illustrative.','', '## B1 — Demand patterns','', '### B1.1 Volume by zone','', 'Zone totals and shares are in `B1_zone_demand.csv`. Highest total-demand zones in this cleaned extract:']
for z,r in zone.head(4).iterrows(): lines.append(f'- **{z}**: {r.total:,.0f} trips, {100*r.total/zone.total.sum():.1f}% of cleaned observed trips, mean {r['mean']:.1f} trips/zone-hour across {int(r.n):,} rows.')
lines += ['', 'Interpretation: observed totals combine demand intensity with how many hours a zone appears in the raw history. Use `zone_hours` and the gap report before ranking zones as if all had identical coverage.','', '### B1.2 Hour-of-day profile by zone type','', 'Hourly profiles by zone are in `B2_hourly_profiles.csv` and `fig05_zone_profiles.png`. The zone labels are normalized; descriptive zone-type groupings are interpretive rather than official classifications. Peaks differ by zone, so a citywide average alone can hide important local patterns.','', '### B1.3 Weekday vs weekend','', 'The weekend-to-weekday mean ratio for each zone is in `B3_weekend_ratio.csv`.']
for z,r in ratio.sort_values('ratio',ascending=False).head(3).iterrows(): lines.append(f'- Weekend-busier candidates: **{z}** ratio {r.ratio:.2f}.')
for z,r in ratio.sort_values('ratio').head(3).iterrows(): lines.append(f'- Weekend-quieter candidates: **{z}** ratio {r.ratio:.2f}.')
lines += ['', 'Ratios are mean trips per observed zone-hour; gaps and unequal operating history can affect comparisons.','', '### B1.4 Trend, January–October','', f'Weekly city totals are in `B1_weekly_city_totals.csv`; first observed weekly total is {weekly.iloc[0]:,.0f} and last observed weekly total is {weekly.iloc[-1]:,.0f}. The full daily series and 7-day mean are in `fig03_demand_trend_with_holidays.png`. Trend and coverage both matter: November is a future period, so a model trained only on earlier levels may under- or over-extrapolate if demand is changing.','', '## B2 — Weather','', '### B2.1 Timezone check','', f'Weather UTC/offset timestamps are converted to Addis Ababa local time (EAT, UTC+03:00). The code tested rain–demand correlation under offsets −5…+5 hours; see `B2_1_clock_shift_test.csv` and `fig06_weather_timezone_check.png`. The selected clock is based on timestamp semantics and format evidence, not just the highest correlation. The training table has weather measurements on approximately {100*tr.temp_c.notna().mean():.1f}% of observed zone-hour rows after the join.','', '### B2.2 Rain effect by zone type','', 'Rain comparisons are in `B2_rain_summary.csv` and `fig07_rain_effect.png`. The analysis compares average demand across rain classes and broad zone groupings; it is observational and can be confounded by hour, weekday, and zone. A more rigorous extension would match rainy hours to dry hours with the same zone, weekday, and hour.','', '### B2.3 Rain dose-response','', 'Rain is binned into none, light (0–2 mm), moderate (2–10 mm), and heavy (>10 mm) classes. The code-generated means and counts are in `B2_rain_summary.csv`; inspect sample counts before interpreting heavy-rain changes. Response need not be proportional, especially in sparse heavy-rain bins.','', '## B3 — Events and calendar','', '### B3.1 Public holidays','', 'Holiday dates and their observed daily totals versus same-weekday non-holiday baselines are in `B3_holiday_effects.csv` and `fig09_holiday_effects.png`. A holiday does not have to reduce demand in every zone; local travel and event activity can offset citywide patterns.','', '### B3.2 Football match event study','', 'The event study figure is `fig08_event_study.png`. The implementation aligns demand around event starts and compares the event-window shape descriptively. Zone aliases and event coverage are imperfect, so sparse event windows are not strong causal estimates.','', '### B3.3 Event type ranking','', 'A rough event-window comparison is saved in `B3_event_type_effects.csv`. It compares trips in matched event windows with same-zone weekday/hour observations outside nearby event dates. Event coverage and zone matching can be sparse; interpret ranking as exploratory, not causal.','', '### B3.4 Cancelled and unlisted events','', f'The supplied calendar has {len(ev)} event rows, including {int(ev.is_cancelled.astype(str).str.lower().isin(["true","1"]).sum())} rows marked cancelled. Cancelled events are excluded from model features. Three high-trip zone-hours outside any detected event window are listed in `B3_unlisted_spikes.csv`; they are candidates for unlisted events, service disruptions, or data artifacts, and the data alone cannot identify the true explanation.','', '## B4 — Operations and data quality','', '### B4.1 Operational variables vs demand','', 'Historical correlations are in `B4_operational_correlations.csv`. `active_drivers` and `avg_wait_min` are likely partly responses to demand and dispatch behavior, while fare may reflect trip mix and time. Correlation is not causation, and these train-only fields are excluded from forecast inputs because they are unavailable for future test hours.','', '### B4.2 Gaps and outages','', 'Coverage by zone is in `B4_gaps_by_zone.csv`; `fig01_gaps_and_missingness.png` visualizes missingness and observed zone-hours. A missing zone-hour may be a true zero, random missing record, outage, or late zone launch. Without an explicit platform-status table, these categories cannot always be distinguished with confidence; the current pipeline does not fabricate target values for missing historical records.','', '### B4.3 Pay-period effect','', 'The code-generated payday comparison is in `B4_pay_period_effect.csv`. It compares average demand near month-end/month-start (days 28–3) with other days. This is an exploratory, not fully detrended causal estimate; if the difference is small or inconsistent by zone, do not keep payday as a strong feature without further time-aware testing.','', '## Key takeaway','', 'Ride demand has strong zone/hour/weekday structure. Weather and event tables provide useful operational context and are required model feature families, but their incremental predictive value should be judged by chronological ablation rather than assumed. The seasonal baseline is strong, so model improvements must be demonstrated against it.']
(R/'B_analysis_report.md').write_text('\n'.join(lines)+'\n')
# export tables
weekly.rename('weekly_trips').to_frame().to_csv(R/'B1_weekly_city_totals.csv')
pd.DataFrame(hol,columns=['holiday','date','observed_trips','same_weekday_baseline','holiday_index']).to_csv(R/'B3_holiday_effects.csv',index=False)
pd.DataFrame(eff,columns=['event_type','event_window_rows','event_mean_trips','comparison_mean_trips','event_to_baseline_ratio']).sort_values('event_to_baseline_ratio',ascending=False).to_csv(R/'B3_event_type_effects.csv',index=False)
sp.to_csv(R/'B3_unlisted_spikes.csv',index=False)
# pay period comparison: crude daily mean by zone
tr['pay_period']=tr.pickup_hour.dt.day.map(lambda d: d>=28 or d<=3)
pay=tr.groupby(['zone','pay_period']).trips.mean().unstack(); pay['payday_to_other_ratio']=pay[True]/pay[False]; pay.to_csv(R/'B4_pay_period_effect.csv')
# A5 proof examples: choose rain, event, public holiday. Export evidence rows from master table.
proof=[]
rainrow=tr[tr.rain_mm.fillna(0)>0].head(1)
eventrow=tr[tr.event_in_window.fillna(0)>0].head(1)
hol_days=set(pd.to_datetime(ev.loc[ev.event_type.eq('public_holiday'),'start'],errors='coerce').dropna().dt.floor('D'))
holidayrow=tr[tr.pickup_hour.dt.floor('D').isin(hol_days)].head(1)
for label,frame in [('rain',rainrow),('event_window',eventrow),('public_holiday',holidayrow)]:
 if len(frame):
  r=frame.iloc[0]; proof.append({'case':label,'zone':r.zone,'pickup_hour_EAT':r.pickup_hour,'trips_target_historical_only':r.trips,'rain_mm':r.get('rain_mm',np.nan),'temp_c':r.get('temp_c',np.nan),'event_count':r.get('event_count',0),'event_in_window':r.get('event_in_window',0),'event_public_holiday':r.get('event_public_holiday',0),'event_football_match':r.get('event_football_match',0)})
pd.DataFrame(proof).to_csv(R/'A5_join_proof_examples.csv',index=False)
print('Reports written',len(lines),'lines; proof rows',len(proof))
