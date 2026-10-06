import streamlit as st
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Ethiopian Crop Yield Forecast",
    page_icon="🌾",
    layout="wide"
)

# Paths
ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "final_model.joblib"
WEATHER_PATH = Path(__file__).parent / "assets" / "cleaned_weather.csv"
PRICE_PATH = Path(__file__).parent / "assets" / "cleaned_prices.csv"
TRAIN_PATH = ROOT / "data" / "processed" / "master_train.csv"

@st.cache_resource
def load_model():
    bundle = joblib.load(MODEL_PATH)
    return bundle["model"], bundle["columns"]

@st.cache_data
def load_data():
    weather = pd.read_csv(WEATHER_PATH)
    prices = pd.read_csv(PRICE_PATH)
    train = pd.read_csv(TRAIN_PATH)
    return weather, prices, train

model, feature_cols = load_model()
weather_df, price_df, train_df = load_data()

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NUM = {m: i + 1 for i, m in enumerate(MONTHS)}

st.title("🌾 Ethiopian Smallholder Crop-Yield Forecast")
st.markdown("Predict plot-level yield and estimated farm revenue with automatic weather and market price lookups.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("📍 Location & Crop Selection")
    region = st.selectbox("Region", sorted(train_df["region"].unique()))
    crop = st.selectbox("Crop Type", sorted(train_df["crop_type"].unique()))
    year = st.selectbox("Survey Year", [2021, 2022, 2023, 2024], index=3)
    month = st.selectbox("Planting Month", ["Feb", "Mar", "Jun", "Jul", "Aug"], index=3)

with col2:
    st.subheader("🌱 Farm & Input Parameters")
    altitude = st.number_input("Altitude (meters)", min_value=0.0, max_value=4000.0, value=1500.0)
    farm_size = st.number_input("Farm Size (hectares)", min_value=0.1, max_value=10.0, value=1.0)
    fertilizer = st.number_input("Fertilizer (kg/ha)", min_value=0.0, max_value=200.0, value=40.0)
    soil_quality = st.slider("Soil Quality Index (0-1)", min_value=0.0, max_value=1.0, value=0.6)
    improved_seed = st.radio("Improved Seed Used?", [0, 1], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)", index=1)
    pest_flag = st.radio("Pest/Disease Pressure?", [0, 1], format_func=lambda x: "Yes (1)" if x == 1 else "No (0)", index=0)
    labor_days = st.number_input("Labor Days per Hectare", min_value=0.0, max_value=200.0, value=40.0)
    distance_market = st.number_input("Distance to Market (km)", min_value=0.0, max_value=100.0, value=10.0)

if st.button("🚀 Calculate Forecast & Revenue", use_container_width=True):
    start_idx = MONTH_NUM[month]
    window_months = [MONTHS[(start_idx - 1 + i) % 12] for i in range(4)]
    
    sub_w = weather_df[(weather_df.region == region) & (weather_df.year == int(year)) & weather_df.month.isin(window_months)]
    
    mean_temp = sub_w.avg_temp_c.mean() if len(sub_w) > 0 else 20.0
    sum_rain = sub_w.monthly_rainfall_mm.sum() if len(sub_w) > 0 else 400.0
    heat_days = sub_w.extreme_heat_days.sum() if len(sub_w) > 0 else 0
    obs_months = len(sub_w)
    
    row = pd.DataFrame([{
        "region": region,
        "crop_type": crop,
        "survey_year": int(year),
        "planting_month": month,
        "altitude_m": float(altitude),
        "rainfall_mm_season": np.nan,
        "farm_size_ha": float(farm_size),
        "fertilizer_kg_per_ha": float(fertilizer),
        "improved_seed_used": int(improved_seed),
        "pest_disease_flag": int(pest_flag),
        "soil_quality_index": float(soil_quality),
        "labor_days_per_ha": float(labor_days),
        "distance_to_market_km": float(distance_market),
        "season_mean_temp": mean_temp,
        "season_rainfall_mm": sum_rain,
        "season_extreme_heat_days": heat_days,
        "weather_months_observed": obs_months,
        "season_temp_std": sub_w.avg_temp_c.std(ddof=0) if len(sub_w) > 0 else 0.0,
        "season_rainfall_std": sub_w.monthly_rainfall_mm.std(ddof=0) if len(sub_w) > 0 else 0.0,
        "season_temp_anomaly": np.nan,
        "planting_month_num": MONTH_NUM[month],
        "fertilizer_seed_interaction": float(fertilizer) * int(improved_seed),
        "rainfall_reporting_ratio": np.nan,
        "temp_rainfall_interaction": mean_temp * np.log1p(sum_rain)
    }])
    
    encoded_row = pd.get_dummies(row, columns=["region", "crop_type", "planting_month"], dtype=float).reindex(columns=feature_cols, fill_value=0)
    pred_yield = float(model.predict(encoded_row)[0])
    
    sub_p = price_df[(price_df.region == region) & (price_df.crop_type == crop) & (price_df.year == int(year))]
    unit_price = float(sub_p.price_birr_per_quintal.iloc[0]) if len(sub_p) > 0 else 4000.0
    
    est_revenue = pred_yield * float(farm_size) * 10 * unit_price
    ref_yield = train_df[(train_df.region == region) & (train_df.crop_type == crop)].yield_tons_per_ha.mean()
    
    st.divider()
    st.subheader("📊 Forecast Results")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Predicted Yield", f"{pred_yield:.2f} t/ha", delta=f"{pred_yield - ref_yield:+.2f} vs region mean")
    r_col2.metric("Estimated Revenue", f"{est_revenue:,.0f} Birr")
    r_col3.metric("Market Price", f"{unit_price:,.0f} Birr/quintal")
    
    st.info(f"**Automatic Lookups:** Seasonal Mean Temp: **{mean_temp:.1f} °C** | Seasonal Rainfall: **{sum_rain:.1f} mm** | Regional Benchmark ({region} × {crop}): **{ref_yield:.2f} t/ha**")
