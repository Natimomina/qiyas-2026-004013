from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import joblib

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from pipeline import FEATURES, norm_zone, parse_local_series

st.set_page_config(page_title='ADDIS / Ride Demand',page_icon='◈',layout='wide',initial_sidebar_state='collapsed')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Manrope',sans-serif} .stApp{background:radial-gradient(circle at 88% 4%,rgba(67,97,238,.18),transparent 27%),radial-gradient(circle at 3% 40%,rgba(45,212,191,.10),transparent 24%),#080d18;color:#f3f5fb}
.block-container{padding-top:1.5rem;max-width:1450px}.hero{padding:30px 34px;border:1px solid rgba(255,255,255,.12);border-radius:24px;background:linear-gradient(115deg,rgba(19,30,52,.96),rgba(19,27,44,.78));margin-bottom:20px;box-shadow:0 24px 80px rgba(0,0,0,.18)}
.eyebrow{font-family:'DM Mono',monospace;text-transform:uppercase;letter-spacing:.16em;color:#72e3d0;font-size:11px}.hero h1{font-size:clamp(32px,4vw,54px);letter-spacing:-.05em;line-height:1.05;margin:14px 0 10px;color:#f7f9ff}.hero p{color:#aebbd1;font-size:15px;max-width:720px}.metric{border:1px solid rgba(255,255,255,.1);background:linear-gradient(145deg,rgba(25,38,62,.88),rgba(16,24,40,.85));padding:20px 22px;border-radius:18px;min-height:118px}.metric .label{color:#9eacc4;font-size:12px;text-transform:uppercase;letter-spacing:.09em}.metric .value{font-size:30px;font-weight:800;letter-spacing:-.04em;margin-top:8px;color:#f7f9ff}.metric .hint{font-size:12px;color:#72e3d0;margin-top:4px}.section{font-size:18px;font-weight:800;letter-spacing:-.025em;margin:16px 0 8px}.note{color:#9eacc4;font-size:12px}.stButton>button{border-radius:12px;border:0;background:linear-gradient(95deg,#66e4cd,#8da8ff);color:#08111f;font-weight:800;padding:.7rem 1.2rem}.stSelectbox label,.stDateInput label{color:#d9e2f2!important}.stDataFrame{border:1px solid rgba(255,255,255,.12);border-radius:12px;overflow:hidden}
</style>''',unsafe_allow_html=True)

@st.cache_resource
def load_bundle(): return joblib.load(ROOT/'models'/'final_model.joblib')
@st.cache_data
def load_data():
    master=pd.read_csv(ROOT/'data/processed/master_test.csv',parse_dates=['pickup_hour'])
    raw=pd.read_csv(ROOT/'data/raw/ride_demand_train.csv')
    raw['zone']=raw.zone.map(norm_zone); raw['avg_fare_birr']=pd.to_numeric(raw.avg_fare_birr,errors='coerce')
    fares=raw.groupby('zone').avg_fare_birr.median().to_dict()
    events=pd.read_csv(ROOT/'reports/B3_cleaned_events.csv')
    return master,fares,events

bundle=load_bundle(); master,fares,events=load_data(); model=bundle['model']; features=bundle['features']
min_date=pd.Timestamp('2025-11-01').date(); max_date=pd.Timestamp('2025-11-14').date()
st.markdown('''<div class="hero"><div class="eyebrow">Qiyas AI Hackathon · Operations Intelligence</div><h1>Ride demand,<br>one hour ahead of the rush.</h1><p>A forecast console for Addis Ababa ride-hailing operations. Explore hourly demand by zone, anticipate peak periods, and translate demand into driver capacity and gross fare estimates.</p></div>''',unsafe_allow_html=True)

col1,col2,col3=st.columns([1,1,1.3])
with col1:
    zones=sorted(master.zone.dropna().unique().tolist()); zone=st.selectbox('Pickup zone',zones,index=zones.index('KAZANCHIS') if 'KAZANCHIS' in zones else 0)
with col2:
    day=st.date_input('Forecast date',value=min_date,min_value=min_date,max_value=max_date)
with col3:
    st.markdown('<div class="note" style="padding-top:38px">Forecast window: <b>1–14 November 2025</b> · Timezone: <b>Africa/Addis_Ababa (EAT, UTC+3)</b></div>',unsafe_allow_html=True)

if day < min_date or day > max_date:
    st.warning('Choose a date from 1 to 14 November 2025, the supported challenge forecast window.')
else:
    day_start=pd.Timestamp(day); day_end=day_start+pd.Timedelta(days=1)
    df=master[(master.zone==zone)&(master.pickup_hour>=day_start)&(master.pickup_hour<day_end)].copy().sort_values('pickup_hour')
    if df.empty:
        st.error('No test rows were found for this zone/date. Check the normalized zone labels in master_test.csv.')
    else:
        df['forecast_trips']=np.clip(model.predict(df[features]),0,None)
        fare=float(fares.get(zone,np.nan)); fare= fare if np.isfinite(fare) else float(pd.Series(list(fares.values())).median())
        df['drivers_needed']=np.ceil(df.forecast_trips/1.3).astype(int)
        df['gross_fare_birr']=df.forecast_trips*fare
        peak=df.loc[df.forecast_trips.idxmax()]
        total=float(df.forecast_trips.sum()); peak_value=float(peak.forecast_trips); peak_hour=peak.pickup_hour.strftime('%H:%M')
        m1,m2,m3,m4=st.columns(4)
        for c,label,value,hint in [(m1,'Forecast trips · 24h',f'{total:,.0f}','Expected requests across the selected day'),(m2,'Peak demand',f'{peak_value:.1f}',f'Peak hour · {peak_hour}'),(m3,'Drivers at peak',f'{int(peak.drivers_needed)}','At 1.3 trips / driver-hour'),(m4,'Gross fare estimate',f'ETB {df.gross_fare_birr.sum():,.0f}',f'Using historical median fare · ETB {fare:,.0f}')]:
            with c: st.markdown(f'<div class="metric"><div class="label">{label}</div><div class="value">{value}</div><div class="hint">{hint}</div></div>',unsafe_allow_html=True)
        left,right=st.columns([1.55,1])
        with left:
            st.markdown('<div class="section">Hourly demand curve</div>',unsafe_allow_html=True)
            fig=go.Figure(); fig.add_trace(go.Scatter(x=df.pickup_hour,y=df.forecast_trips,mode='lines+markers',name='Forecast',line=dict(color='#72e3d0',width=3),marker=dict(size=5),fill='tozeroy',fillcolor='rgba(114,227,208,.10)'))
            typical=master[master.zone.eq(zone)].copy(); typical['hour']=typical.pickup_hour.dt.hour; typical['typical']=typical.groupby('hour').hour.transform('count')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',margin=dict(l=5,r=5,t=20,b=5),height=350,xaxis_title='Hour (EAT)',yaxis_title='Predicted trips',showlegend=False)
            fig.update_xaxes(tickformat='%H:%M',dtick=3*3600000,gridcolor='rgba(255,255,255,.06)'); fig.update_yaxes(gridcolor='rgba(255,255,255,.06)',rangemode='tozero'); st.plotly_chart(fig,use_container_width=True)
        with right:
            st.markdown('<div class="section">Context looked up automatically</div>',unsafe_allow_html=True)
            rain=df[['pickup_hour','rain_mm','temp_c']].copy(); rain=rain.dropna(subset=['rain_mm'])
            if len(rain):
                wet=rain.loc[rain.rain_mm.idxmax()]
                st.markdown(f'<div class="metric"><div class="label">Weather outlook</div><div class="value">{float(wet.rain_mm):.1f} mm</div><div class="hint">Highest hourly rain · {wet.pickup_hour.strftime("%H:%M")} · EAT</div></div>',unsafe_allow_html=True)
            else: st.info('Weather observations are unavailable for some or all hours; the model imputes missing values.')
            day_events=events.copy(); day_events['start']=pd.to_datetime(day_events.start,errors='coerce'); day_events['end']=pd.to_datetime(day_events.end,errors='coerce')
            matched=day_events[(day_events.start<day_end)&(day_events.end>=day_start)&(~day_events.status_clean.astype(str).str.contains('cancel',case=False,na=False))]
            zone_events=matched[matched.zone_norm.astype(str).str.upper().str.contains(zone,regex=False)|matched.zone_norm.astype(str).str.upper().isin(['ALL','ALL ZONES','CITYWIDE','CITY-WIDE'])]
            if len(zone_events):
                for _,e in zone_events.head(4).iterrows(): st.markdown(f'<div class="metric" style="min-height:auto;margin-top:8px;padding:13px 16px"><div class="label">{e.event_type.replace("_"," ").title()}</div><b>{e.event_name}</b><div class="hint">{e.start.strftime("%d %b · %H:%M") if pd.notna(e.start) else "Time TBD"} – {e.end.strftime("%H:%M") if pd.notna(e.end) else "TBD"}</div></div>',unsafe_allow_html=True)
            else: st.markdown('<div class="metric"><div class="label">Event calendar</div><div class="value" style="font-size:18px">No matching event found</div><div class="hint">No active listed event for this zone/date.</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="section">24-hour operations plan</div>',unsafe_allow_html=True)
        table=df[['pickup_hour','forecast_trips','drivers_needed','gross_fare_birr','rain_mm','temp_c','event_count']].copy(); table.columns=['Hour (EAT)','Forecast trips','Drivers needed','Gross fares (ETB)','Rain (mm)','Temp (°C)','Active event signals']; table['Hour (EAT)']=table['Hour (EAT)'].dt.strftime('%H:%M'); table['Forecast trips']=table['Forecast trips'].round(1); table['Gross fares (ETB)']=table['Gross fares (ETB)'].round(0); table['Rain (mm)']=table['Rain (mm)'].round(1); table['Temp (°C)']=table['Temp (°C)'].round(1)
        st.dataframe(table,use_container_width=True,hide_index=True,height=380)
        st.download_button('Export hourly plan as CSV',data=table.to_csv(index=False).encode(),file_name=f'ride_forecast_{zone.lower().replace(" ","_")}_{day}.csv',mime='text/csv')
        st.markdown('<p class="note">Prototype for the Qiyas training challenge using synthetic illustrative data. Forecasts are not guaranteed demand; driver estimates assume approximately 1.3 trips per active driver-hour. Gross fares are estimates using historical median zone fare, not net revenue.</p>',unsafe_allow_html=True)
