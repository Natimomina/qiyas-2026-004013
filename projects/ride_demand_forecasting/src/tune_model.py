"""Small, reproducible chronological RF search. All candidates use the same held-out 14-day window."""
from pathlib import Path
import sys,time
import numpy as np,pandas as pd
from sklearn.metrics import mean_squared_error,mean_absolute_error
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from pipeline import FEATURES,make_model
tr=pd.read_csv(ROOT/'data/processed/master_train.csv',parse_dates=['pickup_hour']).dropna(subset=['trips'])
end=tr.pickup_hour.max().floor('D')+pd.Timedelta(hours=23); start=end.normalize()-pd.Timedelta(days=13)
fit=tr[tr.pickup_hour<start]; val=tr[(tr.pickup_hour>=start)&(tr.pickup_hour<=end)]
fs=fit.sample(min(22000,len(fit)),random_state=42); results=[]
configs=[(16,10,4),(24,12,4),(32,12,3),(24,14,5)]
for n,depth,leaf in configs:
 m=make_model('rf'); m.set_params(model__n_estimators=n,model__max_depth=depth,model__min_samples_leaf=leaf)
 t=time.time(); m.fit(fs[FEATURES],fs.trips); p=np.clip(m.predict(val[FEATURES]),0,None)
 results.append({'n_estimators':n,'max_depth':depth,'min_samples_leaf':leaf,'fit_rows':len(fs),'validation_rows':len(val),'RMSE':float(np.sqrt(mean_squared_error(val.trips,p))),'MAE':float(mean_absolute_error(val.trips,p)),'train_seconds':time.time()-t})
out=pd.DataFrame(results).sort_values('RMSE'); out.to_csv(ROOT/'reports/D6_tuning.csv',index=False); print(out.to_string(index=False))
