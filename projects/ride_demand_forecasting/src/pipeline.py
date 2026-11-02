from __future__ import annotations
from pathlib import Path
import re, json, time, warnings
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import HistGradientBoostingRegressor, ExtraTreesRegressor, RandomForestRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance
import joblib

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'; PROC=ROOT/'data'/'processed'; FIG=ROOT/'figures'; REPORT=ROOT/'reports'; MODELS=ROOT/'models'
ZONES=['AYAT','ARAT KILO','BOLE','CMC','GERJI','KAZANCHIS','KOLFE','LIDETA','MEGENAGNA','MERKATO','PIASSA','SARB​ET'.replace('\u200b','')]
ZONE_ALIASES={'AYAT':'AYAT','ARAT KILO':'ARAT KILO','ARAT  KILO':'ARAT KILO','BOLE':'BOLE','BOLE RD':'BOLE','C.M.C':'CMC','CMC':'CMC','GERJI':'GERJI','KAZANCHES':'KAZANCHIS','KAZANCHIS':'KAZANCHIS','KOLFE':'KOLFE','KOLFE KERANIO':'KOLFE','LIDETA':'LIDETA','MEGENAGA':'MEGENAGNA','MEGENAGNA':'MEGENAGNA','MERKATO':'MERKATO','MERCATO':'MERKATO','PIASSA':'PIASSA','PIAZZA':'PIASSA','SARB​ET':'SARB​ET','SARBET':'SARBET'}
ZONE_ALIASES={k.replace('\u200b',''):v.replace('\u200b','') for k,v in ZONE_ALIASES.items()}
EVENT_ALIASES={'PUBLIC HOLIDAY':'public_holiday','SCHOOL BREAK':'school_break','FOOTBALL MATCH':'football_match','CONCERT':'concert','CONFERENCE':'conference','EXHIBITION':'exhibition','ROAD CLOSURE':'road_closure','SPORTS RUN':'sports_run'}

def parse_local_series(series, weather=False):
    """Parse mixed timestamp strings. Offset/Z timestamps are converted to Africa/Addis_Ababa; naive timestamps are interpreted as local EAT."""
    out=[]
    for v in series.astype('string'):
        if pd.isna(v) or not str(v).strip(): out.append(pd.NaT); continue
        s=str(v).strip()
        try:
            # Explicit UTC/offset strings carry their own clock; convert to Addis local time.
            if re.search(r'(Z|[+-]\d\d:\d\d)$',s):
                t=pd.to_datetime(s,errors='coerce',utc=True)
                if pd.isna(t): out.append(pd.NaT)
                else: out.append(t.tz_convert('Africa/Addis_Ababa').tz_localize(None))
            else:
                t=pd.to_datetime(s,errors='coerce',dayfirst=True,format='mixed')
                out.append(pd.Timestamp(t).to_pydatetime().replace(tzinfo=None) if not pd.isna(t) else pd.NaT)
        except Exception: out.append(pd.NaT)
    return pd.to_datetime(pd.Series(out,index=series.index),errors='coerce').dt.floor('h')

def norm_zone(x):
    if pd.isna(x): return np.nan
    s=re.sub(r'\s+',' ',str(x).strip().upper())
    # Event descriptions may append subcity/extra text; map known prefixes and multi-zone phrases separately.
    if s in ZONE_ALIASES: return ZONE_ALIASES[s]
    for suffix in [' (KIRKOS)',' (BOLE SUBCITY)',' (ARADA)']:
        s=s.replace(suffix,'')
    return ZONE_ALIASES.get(s,s)

def norm_event_type(x):
    if pd.isna(x): return 'unknown'
    s=re.sub(r'\s+',' ',str(x).strip().lower()).replace(' ','_')
    return {'public_holiday':'public_holiday','school_break':'school_break','football_match':'football_match','concert':'concert','conference':'conference','exhibition':'exhibition','road_closure':'road_closure','sports_run':'sports_run'}.get(s,s)

def load_raw():
    train=pd.read_csv(RAW/'ride_demand_train.csv')
    test=pd.read_csv(RAW/'ride_demand_test.csv')
    weather=pd.read_csv(RAW/'weather_hourly.csv')
    events=pd.read_csv(RAW/'events_calendar.csv')
    return train,test,weather,events

def clean_tables(train,test,weather,events):
    log=[]
    def issue(file,col,kind,n,fix,why): log.append({'file':file,'column(s)':col,'issue_type':kind,'rows_affected':int(n),'percent_of_file':round(100*n/max(1,{'train':len(train),'test':len(test),'weather':len(weather),'events':len(events)}.get(file,1)),3),'fix_applied':fix,'reason':why})
    tr=train.copy(); te=test.copy(); we=weather.copy(); ev=events.copy()
    for df,file,col in [(tr,'train','zone'),(te,'test','zone'),(we,'weather','timestamp'),(ev,'events','zone')]: pass
    # zones and mixed timestamps
    tr['zone_raw']=tr['zone']; tr['zone']=tr['zone'].map(norm_zone)
    te['zone_raw']=te['zone']; te['zone']=te['zone'].map(norm_zone)
    ev['zone_raw']=ev['zone']; ev['zone_norm']=ev['zone'].map(norm_zone)
    tr['pickup_hour_raw']=tr['pickup_hour']; tr['pickup_hour']=parse_local_series(tr['pickup_hour'])
    te['pickup_hour_raw']=te['pickup_hour']; te['pickup_hour']=parse_local_series(te['pickup_hour'])
    we['timestamp_raw']=we['timestamp']; we['pickup_hour']=parse_local_series(we['timestamp'],weather=True)
    # parse event intervals as naive Addis local time; event timestamps are local per instructions
    ev['start_raw']=ev['start_datetime']; ev['end_raw']=ev['end_datetime']
    ev['start']=parse_local_series(ev['start_datetime']); ev['end']=parse_local_series(ev['end_datetime'])
    # Resolve ambiguous slash dates using the paired endpoint when the other endpoint is explicit.
    def local_candidate(value, dayfirst):
        try:
            t=pd.to_datetime(str(value),errors='coerce',dayfirst=dayfirst,format='mixed')
            return pd.Timestamp(t).floor('h') if not pd.isna(t) else pd.NaT
        except Exception: return pd.NaT
    for ix,row in ev.iterrows():
        ss=str(row.get('start_datetime','')); ee=str(row.get('end_datetime',''))
        s_amb=bool(re.match(r'^\d{1,2}/\d{1,2}/\d{4}',ss)) and int(ss.split('/')[0])<=12 and int(ss.split('/')[1])<=12
        e_amb=bool(re.match(r'^\d{1,2}/\d{1,2}/\d{4}',ee)) and int(ee.split('/')[0])<=12 and int(ee.split('/')[1])<=12
        if s_amb and not e_amb and pd.notna(ev.at[ix,'end']):
            cs=[local_candidate(ss,True),local_candidate(ss,False)]
            good=[c for c in cs if pd.notna(c) and pd.Timedelta(0)<=ev.at[ix,'end']-c<=pd.Timedelta(days=7)]
            if good: ev.at[ix,'start']=min(good,key=lambda c:abs((ev.at[ix,'end']-c).total_seconds()))
        elif e_amb and not s_amb and pd.notna(ev.at[ix,'start']):
            cs=[local_candidate(ee,True),local_candidate(ee,False)]
            good=[c for c in cs if pd.notna(c) and pd.Timedelta(0)<=c-ev.at[ix,'start']<=pd.Timedelta(days=7)]
            if good: ev.at[ix,'end']=min(good,key=lambda c:abs((c-ev.at[ix,'start']).total_seconds()))
    ev['event_type_raw']=ev['event_type']; ev['event_type']=ev['event_type'].map(norm_event_type)
    ev['status_clean']=ev['status'].astype('string').str.strip().str.lower()
    ev['expected_attendance_num']=pd.to_numeric(ev['expected_attendance'].astype('string').str.replace(',','',regex=False).str.extract(r'(\d+(?:\.\d+)?)')[0],errors='coerce')
    issue('events','expected_attendance','missing or free-text attendance',int(ev['expected_attendance_num'].isna().sum()),'parse numeric attendance where available; otherwise retain as missing','Attendance is optional and should not be fabricated')
    issue('events','event_id','duplicate event identifiers',int(ev['event_id'].duplicated().sum()),'retain rows for audit but avoid treating IDs as model features','Duplicate IDs can make event audit ambiguous')
    # trip target cleaning
    tr['trips_raw']=pd.to_numeric(tr['trips'],errors='coerce')
    neg=(tr['trips_raw']<0).sum(); issue('train','trips','negative/impossible target',neg,'set to missing, then exclude from supervised fitting','Trip counts cannot be negative')
    tr.loc[tr['trips_raw']<0,'trips_raw']=np.nan
    # operational columns retained for analysis, never model features
    for c in ['avg_fare_birr','avg_wait_min','active_drivers']:
        tr[c]=pd.to_numeric(tr[c],errors='coerce')
    # impossible ops values
    for c in ['avg_fare_birr','avg_wait_min','active_drivers']:
        bad=(tr[c]<0).sum(); issue('train',c,'negative operational values',bad,'set to missing','Negative values are not physically meaningful')
        tr.loc[tr[c]<0,c]=np.nan
    # remove invalid times/zones and deduplicate zone-hour, aggregating target median
    issue('train','zone/pickup_hour','unparseable key values',int((tr['zone'].isna()|tr['pickup_hour'].isna()).sum()),'exclude from modeling after audit','A valid zone-hour is required')
    issue('weather','timestamp','unparseable timestamps',int(we['pickup_hour'].isna().sum()),'exclude invalid timestamps','Cannot safely join without a parsed hour')
    # weather sentinels / impossible ranges
    for c in ['temp_c','rain_mm','humidity_pct','wind_kmh']:
        we[c]=pd.to_numeric(we[c],errors='coerce')
    for c,mask,fix in [
        ('temp_c',(we['temp_c']<-10)|(we['temp_c']>55),'set impossible temperatures to missing'),
        ('rain_mm',(we['rain_mm']<0)|(we['rain_mm']>300),'set impossible rainfall to missing'),
        ('humidity_pct',(we['humidity_pct']<0)|(we['humidity_pct']>100),'set outside 0–100 to missing'),
        ('wind_kmh',(we['wind_kmh']<0)|(we['wind_kmh']>150),'set impossible wind speed to missing')]:
        n=int(mask.sum()); issue('weather',c,'impossible/sentinel-like values',n,fix,'Keep plausible measurements; avoid treating error codes as real weather'); we.loc[mask,c]=np.nan
    # duplicate weather hours: aggregate numeric values to one row per hour, retain forecast if present
    we['is_forecast']=we['data_type'].astype(str).str.lower().str.strip().eq('forecast')
    we=we.dropna(subset=['pickup_hour']).groupby('pickup_hour',as_index=False).agg(temp_c=('temp_c','median'),rain_mm=('rain_mm','median'),humidity_pct=('humidity_pct','median'),wind_kmh=('wind_kmh','median'),is_forecast=('is_forecast','max'),weather_rows=('timestamp','size'))
    # event end fixes
    badend=ev['end'].isna() | (ev['end']<ev['start'])
    issue('events','end_datetime','missing/earlier-than-start event ends',int(badend.sum()),'impute missing end as start+2h; clamp earlier ends to start+2h','Create a nonnegative event interval without inventing long durations')
    ev.loc[ev['start'].notna() & ev['end'].isna(),'end']=ev.loc[ev['start'].notna() & ev['end'].isna(),'start']+pd.Timedelta(hours=2)
    ev.loc[ev['start'].notna() & ev['end'].notna() & (ev['end']<ev['start']),'end']=ev.loc[ev['start'].notna() & ev['end'].notna() & (ev['end']<ev['start']),'start']+pd.Timedelta(hours=2)
    issue('events','start_datetime/end_datetime','unparseable event start',int(ev['start'].isna().sum()),'exclude event from interval features but retain in cleaning log','Cannot define event window without start')
    # statuses
    ev['is_cancelled']=ev['status_clean'].str.contains('cancel',na=False)
    # issue log basics
    issue('train','zone','inconsistent zone labels',int((tr['zone_raw'].astype(str)!=tr['zone'].astype(str)).sum()),'normalize aliases/case/whitespace to 12 canonical labels','Make joins and grouped analysis consistent')
    issue('test','zone','inconsistent zone labels',int((te['zone_raw'].astype(str)!=te['zone'].astype(str)).sum()),'same zone normalization as train','Avoid train/test category mismatch')
    issue('events','event_type/zone','inconsistent event labels',int((ev['event_type_raw'].astype(str)!=ev['event_type'].astype(str)).sum()),'normalize event type and zone labels','Enable consistent event features')
    issue('weather','pickup_hour','duplicate timestamps',int(we['weather_rows'].sum()-len(we)),'aggregate duplicate timestamps by median; forecast flag retained if any row forecast','Enforce many-to-one weather join')
    # dedup train by zone-hour using median target; ops medians; test preserve row ids but normalize
    tr=tr.dropna(subset=['zone','pickup_hour'])
    tr=tr.groupby(['zone','pickup_hour'],as_index=False).agg(record_id=('record_id','first'),trips=('trips_raw','median'),avg_fare_birr=('avg_fare_birr','median'),avg_wait_min=('avg_wait_min','median'),active_drivers=('active_drivers','median'))
    te=te.dropna(subset=['zone','pickup_hour']).copy()
    return tr,te,we,ev,pd.DataFrame(log),train,test,weather,events

def attach_events(df, events, pre_hours=2, post_hours=2):
    out=df.copy(); n=len(out)
    out['event_count']=0; out['event_in_window']=0; out['event_hours_to_start']=np.nan; out['event_hours_since_end']=np.nan
    for typ in ['public_holiday','school_break','football_match','concert','conference','exhibition','road_closure','sports_run']:
        out[f'event_{typ}']=0
    valid=events[events['start'].notna() & ~events['is_cancelled']].copy()
    # Parse event zones that may refer to multiple zones or citywide
    for _,e in valid.iterrows():
        zone_text=str(e.get('zone_norm',''))
        is_city=any(x in zone_text.lower() for x in ['citywide','city-wide','all zones','all'])
        affected=[]
        if is_city: affected=out.index.tolist()
        else:
            for z in ZONES:
                if z in zone_text.replace('C.M.C','CMC').replace('PIAZZA','PIASSA').replace('MERCATO','MERKATO').replace('KAZANCHES','KAZANCHIS').replace('MEGENAGA','MEGENAGNA'):
                    affected.extend(out.index[out['zone'].eq(z)].tolist())
            # exact normalized zone
            if zone_text in ZONES: affected.extend(out.index[out['zone'].eq(zone_text)].tolist())
        affected=list(dict.fromkeys(affected))
        if not affected: continue
        start=e['start']; end=e['end']; typ=e['event_type']
        times=out.loc[affected,'pickup_hour']
        # window captures 2h before through 2h after event end
        mask=(times>=start-pd.Timedelta(hours=pre_hours)) & (times<=end+pd.Timedelta(hours=post_hours))
        ids=times.index[mask]
        if len(ids)==0: continue
        out.loc[ids,'event_count']+=1; out.loc[ids,'event_in_window']=1
        if f'event_{typ}' in out.columns: out.loc[ids,f'event_{typ}']=1
        tostart=((start-times.loc[ids]).dt.total_seconds()/3600).clip(lower=0)
        sinceend=((times.loc[ids]-end).dt.total_seconds()/3600).clip(lower=0)
        # nearest event timing signals
        old=out.loc[ids,'event_hours_to_start']; out.loc[ids,'event_hours_to_start']=np.where(old.isna(),tostart,np.minimum(old,tostart))
        old2=out.loc[ids,'event_hours_since_end']; out.loc[ids,'event_hours_since_end']=np.where(old2.isna(),sinceend,np.minimum(old2,sinceend))
    out['event_hours_to_start']=out['event_hours_to_start'].fillna(99).clip(upper=99)
    out['event_hours_since_end']=out['event_hours_since_end'].fillna(99).clip(upper=99)
    return out

def engineer_features(df, weather, events):
    out=df.copy(); out['pickup_hour']=pd.to_datetime(out['pickup_hour']).dt.floor('h')
    out=out.merge(weather[['pickup_hour','temp_c','rain_mm','humidity_pct','wind_kmh','is_forecast']],on='pickup_hour',how='left',validate='many_to_one')
    out['weather_missing']=out[['temp_c','rain_mm','humidity_pct','wind_kmh']].isna().any(axis=1).astype(int)
    out['rain_mm']=out['rain_mm'].clip(lower=0)
    out['rain_class']=pd.cut(out['rain_mm'].fillna(0),[-0.001,0,2,10,1e9],labels=['none','light','moderate','heavy']).astype(str)
    out=attach_events(out,events)
    t=out['pickup_hour']
    out['hour']=t.dt.hour; out['day_of_week']=t.dt.dayofweek; out['is_weekend']=(t.dt.dayofweek>=5).astype(int)
    out['day']=t.dt.day; out['month']=t.dt.month; out['week_of_year']=t.dt.isocalendar().week.astype(int)
    out['is_month_start']=(t.dt.day<=3).astype(int); out['is_month_end']=(t.dt.day>=28).astype(int)
    out['day_of_year']=t.dt.dayofyear; out['trend_days']=(t-t.min()).dt.total_seconds()/86400
    out['hour_sin']=np.sin(2*np.pi*out['hour']/24); out['hour_cos']=np.cos(2*np.pi*out['hour']/24)
    out['dow_sin']=np.sin(2*np.pi*out['day_of_week']/7); out['dow_cos']=np.cos(2*np.pi*out['day_of_week']/7)
    out['zone']=out['zone'].astype(str).str.upper().str.strip()
    # no train-only operational variables are model features
    return out

CAT_FEATURES=['zone','rain_class']
NUM_FEATURES=['hour','day_of_week','is_weekend','day','month','week_of_year','is_month_start','is_month_end','day_of_year','trend_days','hour_sin','hour_cos','dow_sin','dow_cos','temp_c','rain_mm','humidity_pct','wind_kmh','weather_missing','is_forecast','event_count','event_in_window','event_public_holiday','event_school_break','event_football_match','event_concert','event_conference','event_exhibition','event_road_closure','event_sports_run','event_hours_to_start','event_hours_since_end']
FEATURES=CAT_FEATURES+NUM_FEATURES

def make_model(kind='hist',seed=42):
    pre=ColumnTransformer([('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('ohe',OneHotEncoder(handle_unknown='ignore'))]),CAT_FEATURES),('num',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler(with_mean=False))]),NUM_FEATURES)],remainder='drop')
    if kind=='ridge': est=Ridge(alpha=3.0)
    elif kind=='extra': est=ExtraTreesRegressor(n_estimators=24,min_samples_leaf=5,max_features=0.9,max_depth=14,n_jobs=-1,random_state=seed)
    elif kind=='rf': est=RandomForestRegressor(n_estimators=24,min_samples_leaf=5,max_features=0.9,max_depth=14,n_jobs=-1,random_state=seed)
    else: est=HistGradientBoostingRegressor(max_iter=35,learning_rate=0.08,max_leaf_nodes=15,l2_regularization=1.0,random_state=seed)
    # HistGradientBoosting can't consume sparse one-hot; use dense for it
    if kind=='hist':
        pre=ColumnTransformer([('cat',Pipeline([('imputer',SimpleImputer(strategy='most_frequent')),('ohe',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),CAT_FEATURES),('num',Pipeline([('imputer',SimpleImputer(strategy='median'))]),NUM_FEATURES)],remainder='drop')
    return Pipeline([('preprocess',pre),('model',est)])

def metric(y,p): return {'RMSE':float(np.sqrt(mean_squared_error(y,p))),'MAE':float(mean_absolute_error(y,p)),'R2':float(r2_score(y,p))}

def run_pipeline(run_models=True):
    PROC.mkdir(parents=True,exist_ok=True); FIG.mkdir(exist_ok=True); REPORT.mkdir(exist_ok=True); MODELS.mkdir(exist_ok=True)
    train0,test0,weather0,events0=load_raw()
    tr,te,we,ev,log,rawtr,rawte,raww,rawe=clean_tables(train0,test0,weather0,events0)
    # preserve test order and original ids
    te_order=test0[['row_id','zone','pickup_hour']].copy(); te_order['zone']=te_order['zone'].map(norm_zone); te_order['pickup_hour']=parse_local_series(te_order['pickup_hour'])
    # weather+event features; event target time window in local Addis time
    trf=engineer_features(tr,we,ev)
    tebase=te_order.rename(columns={'row_id':'record_id'}).copy(); tef=engineer_features(tebase,we,ev)
    # Data integrity reports
    log.to_csv(REPORT/'A1_cleaning_log.csv',index=False)
    we.to_csv(PROC/'weather_hourly_clean.csv',index=False); ev.to_csv(PROC/'events_calendar_clean.csv',index=False)
    pd.DataFrame({'raw_train_zone_values':pd.Series(rawtr['zone'].dropna().astype(str).unique()),'normalized_train_zone_values':pd.Series(sorted(tr['zone'].unique()))}).to_csv(REPORT/'A2_zone_normalization.csv',index=False)
    # output processed master tables (test excludes target and operational fields)
    train_export=trf[list(dict.fromkeys(['record_id','zone','pickup_hour','trips']+FEATURES))].copy(); test_export=tef[list(dict.fromkeys(['record_id','zone','pickup_hour']+FEATURES))].copy()
    train_export.to_csv(PROC/'master_train.csv',index=False); test_export.to_csv(PROC/'master_test.csv',index=False)
    dictionary=[]
    for c in trf.columns:
        source='derived' if c not in tr.columns else ('ride_demand_train.csv' if c not in ['zone','pickup_hour'] else 'ride_demand_train.csv (normalized)')
        desc={'trips':'Target: requested trips in this zone-hour; excluded from test.','zone':'Canonicalized pickup zone.','pickup_hour':'Hourly timestamp in Addis Ababa local time (EAT).','temp_c':'Hourly temperature, weather timestamp aligned to EAT.','rain_mm':'Hourly rainfall, impossible values removed.','humidity_pct':'Relative humidity percent.','wind_kmh':'Wind speed in km/h.','event_in_window':'1 if a non-cancelled event affects the zone in the event window (-2h to end+2h).','event_hours_to_start':'Hours until nearest relevant event starts; 99 if none within feature set.','event_hours_since_end':'Hours since nearest relevant event ended; 99 if no relevant event.','trend_days':'Elapsed days since earliest timestamp in the feature frame; trend proxy.'}.get(c,f'Column {c} from source or engineered calendar/event/weather feature.')
        dictionary.append({'column':c,'dtype':str(trf[c].dtype),'source':source,'description':desc,'derivation':'See src/pipeline.py; all engineered predictors use calendar, weather forecast/observations, or events known by forecast time.'})
    pd.DataFrame(dictionary).to_csv(PROC/'data_dictionary_master.csv',index=False)
    # Join audits and feature availability
    weather_match=trf['temp_c'].notna().mean()
    matched_events=0
    for _,ee in ev.iterrows():
        if pd.isna(ee.get('start')) or bool(ee.get('is_cancelled',False)): continue
        ztxt=str(ee.get('zone_norm','')).upper(); city=any(x in ztxt.lower() for x in ['citywide','city-wide','all zones','all'])
        if city: candidates=trf
        else:
            zn=next((z for z in ZONES if z in ztxt.replace('C.M.C','CMC').replace('PIAZZA','PIASSA').replace('MERCATO','MERKATO').replace('KAZANCHES','KAZANCHIS').replace('MEGENAGA','MEGENAGNA')),None)
            candidates=trf[trf.zone.eq(zn)] if zn else trf.iloc[0:0]
        if len(candidates) and ((candidates.pickup_hour>=ee['start']-pd.Timedelta(hours=2))&(candidates.pickup_hour<=ee['end']+pd.Timedelta(hours=2))).any(): matched_events+=1
    audit={'train_rows_after_dedup':len(trf),'test_rows':len(tef),'weather_unique_hours':len(we),'weather_match_rate_train':float(weather_match),'weather_missing_zone_hours':int(trf['temp_c'].isna().sum()),'train_duplicate_zone_hours_after_cleaning':int(trf.duplicated(['zone','pickup_hour']).sum()),'test_duplicate_zone_hours':int(tef.duplicated(['zone','pickup_hour']).sum()),'events_total':len(ev),'events_cancelled':int(ev['is_cancelled'].sum()),'events_with_valid_start':int(ev['start'].notna().sum()),'events_matched_at_least_one_zone_hour':int(matched_events),'events_unmatched_or_excluded':int(len(ev)-matched_events),'timezone_policy':'Offset/Z weather timestamps converted to Africa/Addis_Ababa (UTC+03:00); naive trip and event times interpreted as Addis local time.','event_window':'2 hours before event start through 2 hours after event end; cancelled events excluded.'}
    (REPORT/'A_join_audit.json').write_text(json.dumps(audit,indent=2))
    checks=[]
    def check(name,cond,detail): checks.append({'check':name,'status':'PASS' if cond else 'FAIL','detail':detail})
    check('train zone-hour unique',not trf.duplicated(['zone','pickup_hour']).any(),f'{trf.duplicated(["zone","pickup_hour"]).sum()} duplicate keys')
    check('test row count preserved',len(tef)==len(test0),f'{len(tef)} processed vs {len(test0)} input')
    check('test row ids unique',tef['record_id'].is_unique,'Each row_id appears once')
    check('12 canonical zones',set(trf.zone.unique()).issubset(set(ZONES)) and len(trf.zone.unique())==12,f'{trf.zone.nunique()} train zones')
    check('no negative target',not (trf.trips.dropna()<0).any(),'Negative targets excluded')
    check('forecast-time feature policy',not any(c in FEATURES for c in ['avg_fare_birr','avg_wait_min','active_drivers']),'Operational-only columns excluded')
    check('weather join many-to-one',we['pickup_hour'].is_unique,'Weather aggregated to one row per hour')
    pd.DataFrame(checks).to_csv(REPORT/'A7_integrity_checks.csv',index=False)
    # analysis summary
    valid=trf.dropna(subset=['trips']).copy(); valid['date']=valid['pickup_hour'].dt.date
    zone_summary=valid.groupby('zone').agg(total_trips=('trips','sum'),mean_trips=('trips','mean'),zone_hours=('trips','count')).sort_values('total_trips',ascending=False)
    zone_summary['city_share_pct']=100*zone_summary.total_trips/zone_summary.total_trips.sum(); zone_summary.to_csv(REPORT/'B1_zone_demand.csv')
    valid['weekday']=valid.pickup_hour.dt.dayofweek; valid['hour']=valid.pickup_hour.dt.hour
    profiles=valid.groupby(['zone','weekday','hour']).trips.mean().reset_index(); profiles.to_csv(REPORT/'B2_hourly_profiles.csv',index=False)
    valid['is_weekend']=valid.weekday>=5
    weekend=valid.groupby(['zone','is_weekend']).trips.mean().unstack(); weekend['weekend_weekday_ratio']=weekend.get(True,np.nan)/weekend.get(False,np.nan); weekend.to_csv(REPORT/'B3_weekend_ratio.csv')
    # weather clock correlation shifts
    # compare merged trips to weather shifted by k hours
    clock=[]
    tmp=valid[['zone','pickup_hour','trips']].merge(we[['pickup_hour','rain_mm','temp_c']],on='pickup_hour',how='left')
    for shift in range(-5,6):
        w=we[['pickup_hour','rain_mm']].copy(); w['pickup_hour']=w['pickup_hour']+pd.Timedelta(hours=shift)
        m=valid[['pickup_hour','trips']].merge(w,on='pickup_hour',how='left').dropna()
        corr=m['trips'].corr(m['rain_mm']) if len(m)>5 else np.nan
        clock.append({'weather_hour_shifted_by':shift,'rows':len(m),'rain_demand_correlation':corr})
    pd.DataFrame(clock).to_csv(REPORT/'B2_1_clock_shift_test.csv',index=False)
    # Rain classes by zone
    tmp['rain_class']=pd.cut(tmp.rain_mm.fillna(0),[-.001,0,2,10,1e6],labels=['none','light','moderate','heavy'])
    rain=tmp.groupby('rain_class',observed=False).trips.agg(['mean','count']).reset_index(); rain.to_csv(REPORT/'B2_rain_summary.csv',index=False)
    # event/holiday counts and correlations
    ev[['event_id','event_name','event_type','zone_norm','start','end','status_clean','is_cancelled']].to_csv(REPORT/'B3_cleaned_events.csv',index=False)
    op=rawtr.copy()
    for c in ['trips','avg_fare_birr','avg_wait_min','active_drivers']:
        op[c]=pd.to_numeric(op[c],errors='coerce')
    opcorr=op[['trips','avg_fare_birr','avg_wait_min','active_drivers']].corr(numeric_only=True); opcorr.to_csv(REPORT/'B4_operational_correlations.csv')
    # gap summary by zone/hour grid
    grid=pd.MultiIndex.from_product([sorted(trf.zone.unique()),pd.date_range('2025-01-01', '2025-10-31 23:00',freq='h')],names=['zone','pickup_hour']).to_frame(index=False)
    present=trf[['zone','pickup_hour']].drop_duplicates().assign(present=1)
    gaps=grid.merge(present,on=['zone','pickup_hour'],how='left'); gaps['present']=gaps.present.fillna(0).astype(int)
    gap_summary=gaps.groupby('zone').present.agg(['sum','count']); gap_summary['missing_hours']=gap_summary['count']-gap_summary['sum']; gap_summary.to_csv(REPORT/'B4_gaps_by_zone.csv')
    # train validation split: final 14 days of available train period
    maxdate=valid.pickup_hour.max().floor('h'); val_start=maxdate.normalize()-pd.Timedelta(days=13)
    fit=trf[(trf.pickup_hour<val_start)&trf.trips.notna()].copy(); val=trf[(trf.pickup_hour>=val_start)&trf.trips.notna()].copy()
    model_results=[]; predictions={}
    if run_models:
        # Baseline mean and zone x weekday x hour seasonal mean fitted on fit only
        mean_pred=np.repeat(fit.trips.mean(),len(val)); model_results.append({'model':'Mean baseline',**metric(val.trips,mean_pred),'train_seconds':0.0})
        seas=fit.assign(dow=fit.pickup_hour.dt.dayofweek,hour=fit.pickup_hour.dt.hour).groupby(['zone','dow','hour']).trips.mean()
        keys=pd.MultiIndex.from_arrays([val.zone,val.pickup_hour.dt.dayofweek,val.pickup_hour.dt.hour]); seasonal=np.array([seas.get(k,fit.trips.mean()) for k in keys]); model_results.append({'model':'Seasonal naive (zone×DOW×hour)',**metric(val.trips,seasonal),'train_seconds':0.0}); predictions['Seasonal naive']=seasonal
        for kind in ['ridge','rf','hist']:
            start=time.time(); model=make_model(kind); fit_sample=fit.sample(min(30000,len(fit)),random_state=42) if kind in ['rf','hist'] else fit; model.fit(fit_sample[FEATURES],fit_sample.trips); secs=time.time()-start; pred=np.clip(model.predict(val[FEATURES]),0,None)
            model_results.append({'model':{'ridge':'Ridge','rf':'Random Forest','hist':'HistGradientBoosting'}[kind],**metric(val.trips,pred),'train_seconds':secs}); predictions[kind]=pred
            if kind=='rf':
                joblib.dump({'model':model,'features':FEATURES,'categorical_features':CAT_FEATURES,'numeric_features':NUM_FEATURES,'zones':ZONES,'validation_start':str(val_start),'validation_end':str(maxdate)},MODELS/'final_model.joblib')
        pd.DataFrame(model_results).to_csv(REPORT/'D_model_comparison.csv',index=False)
        # rolling-origin 4 folds, 14 days each; use HistGradientBoosting + seasonal naive
        max_ts=valid.pickup_hour.max().floor('h'); rolling=[]
        for fold in range(4,0,-1):
            end=max_ts-pd.Timedelta(days=14*(fold-1)); start=end.normalize()-pd.Timedelta(days=13)
            ftrain=trf[(trf.pickup_hour<start)&trf.trips.notna()]; fval=trf[(trf.pickup_hour>=start)&(trf.pickup_hour<=end)&trf.trips.notna()]
            if len(ftrain)<1000 or len(fval)<100: continue
            s=ftrain.assign(dow=ftrain.pickup_hour.dt.dayofweek,hour=ftrain.pickup_hour.dt.hour).groupby(['zone','dow','hour']).trips.mean(); ky=pd.MultiIndex.from_arrays([fval.zone,fval.pickup_hour.dt.dayofweek,fval.pickup_hour.dt.hour]); sp=np.array([s.get(k,ftrain.trips.mean()) for k in ky])
            rolling.append({'fold':fold,'validation_start':str(start),'validation_end':str(end),'model':'Seasonal naive','n':len(fval),**metric(fval.trips,sp)})
            try:
                mm=make_model('rf'); fs=ftrain.sample(min(22000,len(ftrain)),random_state=42); mm.fit(fs[FEATURES],fs.trips); pp=np.clip(mm.predict(fval[FEATURES]),0,None)
                rolling.append({'fold':fold,'validation_start':str(start),'validation_end':str(end),'model':'Random Forest','n':len(fval),**metric(fval.trips,pp)})
            except Exception as ex: rolling.append({'fold':fold,'validation_start':str(start),'validation_end':str(end),'model':'Random Forest','n':len(fval),'RMSE':np.nan,'MAE':np.nan,'R2':np.nan,'error':str(ex)})
        pd.DataFrame(rolling).to_csv(REPORT/'D_rolling_origin.csv',index=False)
        # ablation using same validation split
        ablation=[]
        sets={'calendar_zone_trend':['zone','rain_class']+['hour','day_of_week','is_weekend','day','month','week_of_year','is_month_start','is_month_end','day_of_year','trend_days','hour_sin','hour_cos','dow_sin','dow_cos'],
              'plus_weather':['zone','rain_class']+['hour','day_of_week','is_weekend','day','month','week_of_year','is_month_start','is_month_end','day_of_year','trend_days','hour_sin','hour_cos','dow_sin','dow_cos','temp_c','rain_mm','humidity_pct','wind_kmh','weather_missing','is_forecast'],
              'plus_events':['zone','rain_class']+['hour','day_of_week','is_weekend','day','month','week_of_year','is_month_start','is_month_end','day_of_year','trend_days','hour_sin','hour_cos','dow_sin','dow_cos','event_count','event_in_window','event_public_holiday','event_school_break','event_football_match','event_concert','event_conference','event_exhibition','event_road_closure','event_sports_run','event_hours_to_start','event_hours_since_end'],
              'weather_and_events':FEATURES}
        for name,cols in sets.items():
            cats=[c for c in cols if c in CAT_FEATURES]; nums=[c for c in cols if c not in CAT_FEATURES]
            pre=ColumnTransformer([('cat',Pipeline([('imp',SimpleImputer(strategy='most_frequent')),('ohe',OneHotEncoder(handle_unknown='ignore',sparse_output=False))]),cats),('num',SimpleImputer(strategy='median'),nums)])
            mm=Pipeline([('preprocess',pre),('model',RandomForestRegressor(n_estimators=24,min_samples_leaf=5,max_features=0.9,max_depth=14,n_jobs=-1,random_state=42))])
            fs=fit.sample(min(22000,len(fit)),random_state=42); mm.fit(fs[cols],fs.trips); pp=np.clip(mm.predict(val[cols]),0,None); ablation.append({'feature_set':name,**metric(val.trips,pp)})
        pd.DataFrame(ablation).to_csv(REPORT/'D_ablation.csv',index=False)
        # feature availability audit
        pd.DataFrame([
          {'feature':'zone','known_at_forecast_time':'yes','decision':'include','reason':'zone is part of the test row'},
          {'feature':'pickup_hour / calendar features','known_at_forecast_time':'yes','decision':'include','reason':'forecast timestamp is known'},
          {'feature':'weather variables','known_at_forecast_time':'yes for Nov 1-14 forecast rows','decision':'include','reason':'use forecast rows for target dates; observed weather only for historical features'},
          {'feature':'event features','known_at_forecast_time':'yes for published event calendar','decision':'include','reason':'events and intervals are available in the provided calendar'},
          {'feature':'avg_fare_birr','known_at_forecast_time':'no','decision':'exclude from model','reason':'train-only operational column; future fare not supplied'},
          {'feature':'avg_wait_min','known_at_forecast_time':'no','decision':'exclude from model','reason':'train-only outcome/operational measure'},
          {'feature':'active_drivers','known_at_forecast_time':'no','decision':'exclude from model','reason':'future driver availability is unknown and may respond to demand'},
          {'feature':'trips lag/rolling target','known_at_forecast_time':'only if computed from past','decision':'not used in this baseline feature set','reason':'avoid accidental future target leakage; trend/calendar features are used instead'}
        ]).to_csv(REPORT/'D4_feature_availability_audit.csv',index=False)
        # Error analysis and validation predictions
        best=predictions.get('hist',np.repeat(fit.trips.mean(),len(val)))
        err=val[['zone','pickup_hour','trips']].copy(); err['prediction']=best; err['error']=err.prediction-err.trips; err['abs_error']=err.error.abs(); err['hour']=err.pickup_hour.dt.hour; err['day_type']=np.where(err.pickup_hour.dt.dayofweek>=5,'weekend','weekday')
        err.groupby('zone').agg(RMSE=('error',lambda x:np.sqrt(np.mean(x*x))),MAE=('abs_error','mean'),n=('error','size')).to_csv(REPORT/'D_error_by_zone.csv')
        err.groupby('hour').agg(RMSE=('error',lambda x:np.sqrt(np.mean(x*x))),MAE=('abs_error','mean'),n=('error','size')).to_csv(REPORT/'D_error_by_hour.csv')
        err.nlargest(10,'abs_error').to_csv(REPORT/'D_largest_errors.csv',index=False)
        err.to_csv(PROC/'validation_predictions.csv',index=False)
        # submission predictions using saved final model; ensure original order
        final=make_model('rf'); final_train=trf[trf.trips.notna()].sample(min(40000,trf.trips.notna().sum()),random_state=42); final.fit(final_train[FEATURES],final_train.trips)
        joblib.dump({'model':final,'features':FEATURES,'categorical_features':CAT_FEATURES,'numeric_features':NUM_FEATURES,'zones':ZONES,'trained_until':str(trf.pickup_hour.max())},MODELS/'final_model.joblib')
        pred=np.clip(final.predict(tef[FEATURES]),0,None)
        sub=pd.DataFrame({'row_id':te_order['row_id'],'predicted_trips':pred})
        # Preserve template order/IDs; this assumes te_order came from original test order.
        template=pd.read_csv(RAW/'submission_template.csv')
        sub=template[['row_id']].merge(sub,on='row_id',how='left',validate='one_to_one')
        sub['predicted_trips']=sub['predicted_trips'].fillna(float(trf.trips.mean())).clip(lower=0)
        sub.to_csv(ROOT/'submission'/'team_ride_demand_submission.csv',index=False)
    # create README reports and captions after figures in visualization function
    return {'train':trf,'test':tef,'weather':we,'events':ev,'cleaning_log':log,'audit':audit,'valid':valid}

if __name__=='__main__':
    result=run_pipeline(run_models=True)
    print('Pipeline complete. Train rows:',len(result['train']),'test rows:',len(result['test']))
