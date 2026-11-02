from pathlib import Path
import sys, warnings
import numpy as np, pandas as pd, matplotlib.pyplot as plt, seaborn as sns
ROOT=Path(__file__).resolve().parents[1]; RAW=ROOT/'data/raw'; PROC=ROOT/'data/processed'; FIG=ROOT/'figures'; REP=ROOT/'reports'
sns.set_theme(style='whitegrid',context='notebook',palette='colorblind')
def save(fig,name): fig.tight_layout(); fig.savefig(FIG/name,dpi=160,bbox_inches='tight'); plt.close(fig)
def make_figures():
 FIG.mkdir(exist_ok=True); REP.mkdir(exist_ok=True)
 tr=pd.read_csv(PROC/'master_train.csv',parse_dates=['pickup_hour']); raw=pd.read_csv(RAW/'ride_demand_train.csv'); we=pd.read_csv(PROC/'master_train.csv',usecols=['pickup_hour','rain_mm','temp_c']).drop_duplicates('pickup_hour'); ev=pd.read_csv(REP/'B3_cleaned_events.csv') if (REP/'B3_cleaned_events.csv').exists() else pd.DataFrame()
 tr=tr.dropna(subset=['trips']); tr['hour']=tr.pickup_hour.dt.hour; tr['dow']=tr.pickup_hour.dt.dayofweek; tr['date']=tr.pickup_hour.dt.date; tr['month']=tr.pickup_hour.dt.month
 # 01 missingness and gaps
 fig,ax=plt.subplots(1,2,figsize=(15,5)); miss=raw.isna().mean().sort_values(ascending=False)*100; ax[0].bar(miss.index,miss.values); ax[0].set_title('Raw trip-table missingness'); ax[0].set_ylabel('% missing'); ax[0].tick_params(axis='x',rotation=65)
 pres=tr.groupby('zone').pickup_hour.nunique().sort_values(); ax[1].barh(pres.index,pres.values); ax[1].set_title('Observed zone-hours after cleaning'); ax[1].set_xlabel('Unique hours'); save(fig,'fig01_gaps_and_missingness.png')
 # 02 before after distributions
 fig,ax=plt.subplots(2,2,figsize=(12,8)); ax[0,0].hist(pd.to_numeric(raw.trips,errors='coerce').dropna().clip(upper=150),bins=40); ax[0,0].set_title('Raw trips (clipped at 150 for display)'); ax[0,1].hist(tr.trips.clip(upper=150),bins=40); ax[0,1].set_title('Cleaned trips (display range ≤150)'); wr=pd.read_csv(RAW/'weather_hourly.csv'); ax[1,0].hist(pd.to_numeric(wr.temp_c,errors='coerce').dropna(),bins=35); ax[1,0].set_title('Raw temperature'); ax[1,1].hist(pd.to_numeric(we.temp_c,errors='coerce').dropna(),bins=35); ax[1,1].set_title('Aligned/clean temperature'); save(fig,'fig02_before_after_cleaning.png')
 # 03 trend with holidays
 daily=tr.groupby(tr.pickup_hour.dt.floor('D')).trips.sum(); fig,ax=plt.subplots(figsize=(14,5)); daily.plot(ax=ax,lw=1.3,label='Daily trips'); daily.rolling(7,min_periods=1).mean().plot(ax=ax,lw=2.5,label='7-day mean'); ax.set_title('City-wide daily ride demand, Jan–Oct 2025'); ax.set_ylabel('Trips/day'); ax.set_xlabel('Date'); ax.legend(); save(fig,'fig03_demand_trend_with_holidays.png')
 # 04 heatmap hour x weekday city and zone
 fig,ax=plt.subplots(1,2,figsize=(15,6)); p=tr.pivot_table(index='hour',columns='dow',values='trips',aggfunc='mean'); sns.heatmap(p,ax=ax[0],cmap='crest'); ax[0].set_title('City: mean trips by hour × weekday'); ax[0].set_xlabel('Day of week (Mon=0)'); ax[0].set_ylabel('Hour'); z=tr.zone.value_counts().index[0]; pz=tr[tr.zone==z].pivot_table(index='hour',columns='dow',values='trips',aggfunc='mean'); sns.heatmap(pz,ax=ax[1],cmap='crest'); ax[1].set_title(f'{z}: mean trips by hour × weekday'); ax[1].set_xlabel('Day of week'); ax[1].set_ylabel('Hour'); save(fig,'fig04_hour_by_weekday_heatmap.png')
 # 05 zone profiles weekday/weekend small multiples
 zones=sorted(tr.zone.unique()); fig,axs=plt.subplots(4,3,figsize=(15,14),sharex=True); axs=axs.flatten()
 for i,z in enumerate(zones):
  d=tr[tr.zone==z].copy(); d['day_type']=np.where(d.dow>=5,'Weekend','Weekday')
  for typ,g in d.groupby('day_type'): axs[i].plot(g.groupby('hour').trips.mean().index,g.groupby('hour').trips.mean().values,label=typ)
  axs[i].set_title(z); axs[i].set_xlabel('Hour'); axs[i].set_ylabel('Mean trips')
 axs[0].legend(); save(fig,'fig05_zone_profiles.png')
 # 06 clock check rain corr by shift
 clock=pd.read_csv(REP/'B2_1_clock_shift_test.csv'); fig,ax=plt.subplots(figsize=(9,5)); ax.plot(clock.weather_hour_shifted_by,clock.rain_demand_correlation,marker='o'); ax.axvline(0,ls='--',alpha=.6); ax.set_title('Weather clock sensitivity: rain–demand correlation'); ax.set_xlabel('Weather join shift (hours; 0 = normalized EAT clock)'); ax.set_ylabel('Pearson correlation'); save(fig,'fig06_weather_timezone_check.png')
 # 07 rain effect
 if 'rain_mm' in tr:
  tr['rain_class']=pd.cut(tr.rain_mm.fillna(0),[-.001,0,2,10,1e6],labels=['none','light','moderate','heavy']); rr=tr.groupby(['zone','rain_class'],observed=False).trips.mean().reset_index(); rr['zone_type']=rr.zone.map(lambda x:'market' if x in ['MERKATO','PIASSA','LIDETA'] else 'business/transport' if x in ['BOLE','KAZANCHIS','MEGENAGNA'] else 'residential/mixed'); rr=rr.groupby(['zone_type','rain_class'],observed=False).trips.mean().reset_index(); base=rr[rr.rain_class=='none'][['zone_type','trips']].rename(columns={'trips':'dry_mean'}); rr=rr.merge(base,on='zone_type',how='left'); rr['ratio']=rr.trips/rr.dry_mean; fig,ax=plt.subplots(figsize=(10,5)); sns.lineplot(data=rr,x='rain_class',y='ratio',hue='zone_type',marker='o',ax=ax); ax.axhline(1,ls='--',color='gray'); ax.set_title('Demand ratio by rainfall class and zone type'); ax.set_ylabel('Mean trips / dry-hour mean'); ax.set_xlabel('Rain class'); save(fig,'fig07_rain_effect.png')
 # 08 event study approximate event windows
 fig,ax=plt.subplots(figsize=(10,5)); d=tr.copy(); d['relative_hour']=np.nan
 if not ev.empty:
  for typ in ['football_match','concert']:
   e=ev[(ev.event_type==typ)&(~ev.is_cancelled.astype(bool))].copy() if 'is_cancelled' in ev else ev[ev.event_type==typ]
   vals=[]
   for _,r in e.iterrows():
    start=pd.to_datetime(r.start,errors='coerce')
    if pd.isna(start): continue
    zone=str(r.zone_norm).upper(); affected=d if zone in ['CITYWIDE','CITY-WIDE','ALL','ALL ZONES'] else d[d.zone.eq(zone)]
    for h in range(-6,7):
     v=affected.loc[affected.pickup_hour.eq(start+pd.Timedelta(hours=h)),'trips']
     if len(v): vals.append({'type':typ,'relative_hour':h,'trips':v.mean()})
   if vals:
    vv=pd.DataFrame(vals).groupby('relative_hour').trips.mean(); ax.plot(vv.index,vv.values,marker='o',label=typ)
 if not ax.lines: ax.text(.5,.5,'Event-window estimates are sparse; see event report.',ha='center',va='center',transform=ax.transAxes)
 ax.axvline(0,ls='--',color='gray'); ax.set_title('Demand around selected event starts'); ax.set_xlabel('Hours from event start'); ax.set_ylabel('Mean trips per zone-hour'); ax.legend(); save(fig,'fig08_event_study.png')
 # 09 holiday effect (all public holiday event days vs non-holiday daily average)
 fig,ax=plt.subplots(figsize=(10,5)); holidays=[]
 if not ev.empty:
  e=ev[ev.event_type.eq('public_holiday')]
  for _,r in e.iterrows():
   st=pd.to_datetime(r.start,errors='coerce')
   if pd.isna(st): continue
   day=st.floor('D'); observed=tr.loc[tr.pickup_hour.dt.floor('D').eq(day),'trips'].sum()
   normal=tr.loc[tr.pickup_hour.dt.dayofweek.eq(day.dayofweek)&(~tr.pickup_hour.dt.floor('D').between(day-pd.Timedelta(days=3),day+pd.Timedelta(days=3))),'trips'].sum()
   nd=tr.loc[~tr.pickup_hour.dt.floor('D').between(day-pd.Timedelta(days=3),day+pd.Timedelta(days=3)),'pickup_hour'].dt.floor('D').nunique()
   baseline=normal/max(nd,1); holidays.append({'holiday':r.event_name,'index':observed/baseline if baseline else np.nan})
 if holidays:
  hh=pd.DataFrame(holidays).sort_values('index'); ax.barh(hh.holiday,hh['index']); ax.axvline(1,ls='--',color='gray')
 else: ax.text(.5,.5,'No usable public-holiday rows found.',ha='center',va='center',transform=ax.transAxes)
 ax.set_title('Public-holiday demand index (1 = baseline)'); ax.set_xlabel('Observed holiday daily trips / non-holiday daily average'); save(fig,'fig09_holiday_effects.png')
 # 10 model comparison
 comp=pd.read_csv(REP/'D_model_comparison.csv') if (REP/'D_model_comparison.csv').exists() else pd.DataFrame()
 fig,ax=plt.subplots(figsize=(10,5));
 if not comp.empty: ax.bar(comp['model'],comp['RMSE']); ax.tick_params(axis='x',rotation=20)
 else: ax.text(.5,.5,'Run notebook 04 to generate model comparison.',ha='center',va='center',transform=ax.transAxes)
 ax.set_title('Chronological validation RMSE (lower is better)'); ax.set_ylabel('RMSE (trips per zone-hour)'); save(fig,'fig10_model_comparison.png')
 # 11 forecast vs actual validation
 vp=pd.read_csv(PROC/'validation_predictions.csv',parse_dates=['pickup_hour']) if (PROC/'validation_predictions.csv').exists() else pd.DataFrame()
 fig,ax=plt.subplots(figsize=(13,5));
 if not vp.empty:
  for z in vp.zone.drop_duplicates().head(3):
   g=vp[vp.zone==z].sort_values('pickup_hour'); ax.plot(g.pickup_hour,g.trips,label=f'{z} actual',alpha=.8); ax.plot(g.pickup_hour,g.prediction,label=f'{z} predicted',ls='--',alpha=.8)
 else: ax.text(.5,.5,'Run notebook 04 to generate validation predictions.',ha='center',va='center',transform=ax.transAxes)
 ax.set_title('Actual vs predicted demand on chronological validation window'); ax.set_xlabel('Hour'); ax.set_ylabel('Trips'); ax.legend(ncol=3); save(fig,'fig11_forecast_vs_actual.png')
 # 12 feature importance permutation, use model transform complexity avoided: model's native permutation importance on sample
 fig,ax=plt.subplots(figsize=(10,6));
 try:
  import joblib
  bundle=joblib.load(ROOT/'models/final_model.joblib'); model=bundle['model']; sample=tr.sample(min(1500,len(tr)),random_state=42); X=sample[bundle['features']]; y=sample.trips
  # importance across raw columns is costly; use validation error proxy via feature shuffle on sample
  base=np.sqrt(np.mean((model.predict(X)-y)**2)); imps=[]
  for c in bundle['features']:
   Xp=X.copy(); Xp[c]=np.random.default_rng(42).permutation(Xp[c].values); score=np.sqrt(np.mean((model.predict(Xp)-y)**2)); imps.append((c,score-base))
  imp=pd.DataFrame(imps,columns=['feature','importance']).sort_values('importance').tail(15); ax.barh(imp.feature,imp.importance)
 except Exception as e: ax.text(.5,.5,'Feature importance is generated after final model training.',ha='center',va='center',transform=ax.transAxes)
 ax.set_title('Permutation importance proxy (increase in RMSE after shuffling)'); ax.set_xlabel('Increase in RMSE'); save(fig,'fig12_feature_importance.png')
 captions={
 'fig01_gaps_and_missingness.png':'Raw trip columns contain missing values, and coverage differs by zone; inspect the gap report before interpreting zone totals.',
 'fig02_before_after_cleaning.png':'Cleaning removes invalid target values and aligns weather values; distributions should be interpreted alongside the cleaning log.',
 'fig03_demand_trend_with_holidays.png':'Daily city-wide demand and its seven-day moving average show the level and trend the forecasting model must generalize to.',
 'fig04_hour_by_weekday_heatmap.png':'Hour-by-weekday profiles expose recurring weekly and intraday patterns that support calendar features.',
 'fig05_zone_profiles.png':'Zone-level weekday/weekend curves reveal that demand shape differs across locations.',
 'fig06_weather_timezone_check.png':'The rain–demand correlation changes under shifted joins; use the timestamp evidence and explicit UTC-to-EAT conversion rather than choosing a shift solely by correlation.',
 'fig07_rain_effect.png':'Rain-class ratios compare demand during rainy hours with dry-hour baselines; differences are descriptive, not causal proof.',
 'fig08_event_study.png':'Event-start curves summarize available demand around event times; sparse matching should be reported as a limitation rather than overinterpreted.',
 'fig09_holiday_effects.png':'The holiday index compares observed daily demand with non-holiday days; values above one indicate higher observed volume.',
 'fig10_model_comparison.png':'Chronological validation RMSE compares simple baselines and candidate models on the same later time window.',
 'fig11_forecast_vs_actual.png':'Actual and predicted series on held-out later hours show how well the selected model tracks demand in example zones.',
 'fig12_feature_importance.png':'Permutation importance estimates how much error increases when a feature is shuffled; weather and event features are included in the candidate set.'}
 (FIG/'figure_captions.md').write_text('# Figure captions\n\n'+'\n\n'.join(f'**{k}** — {v}' for k,v in captions.items())+'\n')
if __name__=='__main__': make_figures(); print('12 figures generated in',FIG)
