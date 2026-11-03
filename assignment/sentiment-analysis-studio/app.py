from pathlib import Path
import json
import joblib
import streamlit as st

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "sentiment_pipeline.joblib"
METRICS_PATH = ROOT / "reports" / "metrics.json"

st.set_page_config(
    page_title="Sentiment Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A consistent light theme: avoid Streamlit's default dark widget surfaces.
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root {
  --paper: #f6f7f3;
  --surface: #ffffff;
  --surface-soft: #eef3ec;
  --ink: #1c2924;
  --muted: #66756d;
  --line: #e1e8df;
  --forest: #173b30;
  --forest-2: #245544;
  --lime: #c6f27a;
  --lime-soft: #eff9df;
  --red: #a94332;
  --red-soft: #fff0eb;
  --shadow: 0 10px 30px rgba(26, 53, 41, .055);
}
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'DM Sans', sans-serif !important;
  color: var(--ink) !important;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--paper) !important;
  color: var(--ink) !important;
}
[data-testid="stHeader"] { background: rgba(246,247,243,.94) !important; }
[data-testid="stToolbar"] { background: transparent !important; }
.block-container { max-width: 1240px; padding: 2rem 2.4rem 3.5rem; }
h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; color: var(--ink) !important; letter-spacing: -.035em; }
h1 { font-weight: 800 !important; }
h2, h3 { font-weight: 750 !important; }
p, li, label, span, div { text-wrap: pretty; }
p, li, [data-testid="stMarkdownContainer"] { color: var(--ink); }
[data-testid="stCaptionContainer"], .stCaption, small { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: #edf2eb !important;
  border-right: 1px solid #e0e8de !important;
}
section[data-testid="stSidebar"] > div { background: #edf2eb !important; }
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span { color: var(--ink) !important; }
section[data-testid="stSidebar"] [data-testid="stRadio"] label {
  background: rgba(255,255,255,.62);
  border: 1px solid transparent;
  border-radius: 12px;
  padding: .55rem .7rem;
  margin: .18rem 0;
  color: var(--ink) !important;
  transition: background .15s ease, border-color .15s ease;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
  background: #fff !important; border-color: var(--line) !important;
}
section[data-testid="stSidebar"] [data-testid="stRadio"] label p,
section[data-testid="stSidebar"] [data-testid="stRadio"] label span { color: var(--ink) !important; }

/* Hero and content cards */
.hero {
  position: relative; overflow: hidden;
  background: linear-gradient(118deg, #173b30 0%, #245544 100%);
  color: #fff; padding: 2.7rem 2.8rem; border-radius: 26px;
  box-shadow: 0 16px 36px rgba(23,59,48,.12);
}
.hero:after { content: '✳'; position: absolute; right: 3rem; top: -4.8rem; font-size: 17rem; line-height: 1; color: var(--lime); opacity: .10; pointer-events: none; }
.hero .eyebrow { color: var(--lime); text-transform: uppercase; letter-spacing: .17em; font-size: .72rem; font-weight: 800; }
.hero h1 { color: #fff !important; font-size: clamp(2.2rem, 4vw, 3.35rem); line-height: 1.08; margin: .7rem 0 .8rem; max-width: 760px; }
.hero p { color: #e0ebe4 !important; max-width: 720px; font-size: 1.02rem; line-height: 1.75; margin-bottom: 0; }
.panel, .info-card {
  background: var(--surface); border: 1px solid var(--line); border-radius: 20px;
  padding: 1.35rem 1.5rem; box-shadow: var(--shadow);
}
.panel p, .info-card p { color: var(--muted) !important; line-height: 1.65; }
.kicker { color: var(--forest-2); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }

/* Inputs: force readable light surfaces in every Streamlit version */
.stTextArea label, .stTextInput label, .stSelectbox label, .stRadio label,
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
  color: var(--ink) !important; font-weight: 700 !important;
}
.stTextArea textarea, .stTextInput input,
[data-baseweb="select"] > div,
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div {
  background: #fff !important; color: var(--ink) !important;
  border: 1px solid #dce5dc !important; border-radius: 13px !important;
  box-shadow: none !important;
}
.stTextArea textarea::placeholder, .stTextInput input::placeholder { color: #89958e !important; opacity: 1 !important; }
.stTextArea textarea:focus, .stTextInput input:focus,
[data-baseweb="select"] > div:focus-within,
[data-baseweb="input"] > div:focus-within {
  border-color: #79a98d !important; box-shadow: 0 0 0 3px rgba(121,169,141,.16) !important;
}
[data-baseweb="select"] *, [role="listbox"] *, [role="option"] {
  color: var(--ink) !important;
}
[data-baseweb="popover"], [data-baseweb="menu"] { background: #fff !important; }
[data-baseweb="menu"] li:hover, [role="option"]:hover { background: var(--surface-soft) !important; }

/* Buttons and metrics */
div.stButton > button, div.stDownloadButton > button {
  background: var(--lime) !important; color: #20372b !important;
  border: 1px solid #b6e76b !important; border-radius: 999px !important;
  padding: .68rem 1.35rem !important; font-weight: 800 !important;
  min-height: 2.8rem; transition: transform .15s ease, background .15s ease;
}
div.stButton > button:hover, div.stDownloadButton > button:hover {
  background: #b6e968 !important; color: #20372b !important;
  border-color: #a9dc5b !important; transform: translateY(-1px);
}
div.stButton > button p, div.stDownloadButton > button p { color: #20372b !important; }
[data-testid="stMetric"] {
  background: #fff; border: 1px solid var(--line); border-radius: 16px;
  padding: 1rem 1.1rem; box-shadow: var(--shadow);
}
[data-testid="stMetricLabel"] p { color: var(--muted) !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: var(--forest) !important; font-family: 'Manrope', sans-serif !important; }
.stProgress > div > div { background: var(--forest-2) !important; }

/* Result states */
.result-positive, .result-negative { border-radius: 18px; padding: 1.35rem 1.5rem; }
.result-positive { background: var(--lime-soft); border: 1px solid #d5eab7; color: #25452c; }
.result-negative { background: var(--red-soft); border: 1px solid #f0d0c5; color: #73382e; }
.result-positive h2, .result-negative h2 { margin: .25rem 0 .45rem; }
.result-positive h2 { color: #25452c !important; }
.result-negative h2 { color: #73382e !important; }
.result-positive p, .result-negative p { color: inherit !important; }

/* Dataframe and alerts */
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
[data-testid="stAlert"] { border-radius: 14px; }
footer { visibility: hidden; }
@media (max-width: 760px) {
  .block-container { padding: 1.2rem 1rem 2.5rem; }
  .hero { padding: 1.8rem 1.4rem; border-radius: 20px; }
  .hero:after { right: .4rem; font-size: 10rem; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_metrics():
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


st.sidebar.markdown("<div style='padding:.55rem 0 .8rem'><div style='font-size:1.45rem;font-weight:800;color:#173b30'>✦ Sentiment Studio</div><div style='color:#66756d;font-size:.88rem;margin-top:.25rem'>A compact NLP lab</div></div>", unsafe_allow_html=True)
page = st.sidebar.radio("WORKSPACE", ["Live analyzer", "Model insights", "About the project"], label_visibility="visible")
st.sidebar.divider()
st.sidebar.markdown("<div style='background:#fff;border:1px solid #e1e8df;border-radius:14px;padding:.9rem;color:#66756d;font-size:.82rem;line-height:1.6'><b style='color:#173b30'>PROJECT STACK</b><br>TF-IDF · Classical machine learning<br>Built as an interactive NLP demo</div>", unsafe_allow_html=True)

if not MODEL_PATH.exists() or not METRICS_PATH.exists():
    st.error("Model files are missing. Run `python src/train.py` from the project folder first.")
    st.stop()

model, metrics = load_model(), load_metrics()

if page == "Live analyzer":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">TEXT INTELLIGENCE · 01</div>
      <h1>Read the feeling<br>behind the words.</h1>
      <p>Explore the sentiment of a review, comment, or short message. Enter text below and the model will estimate whether it expresses a positive or negative opinion.</p>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    left, right = st.columns([1.25, .75], gap="large")
    with left:
        st.markdown("### Try a sentence")
        examples = {
            "Positive example": "The service was wonderful and the food was absolutely delicious.",
            "Negative example": "I waited for an hour and the product stopped working the next day.",
            "Mixed example": "The design is beautiful, but the battery life is disappointing.",
        }
        chosen = st.selectbox("Quick examples", ["Write my own"] + list(examples))
        default = "" if chosen == "Write my own" else examples[chosen]
        text_input = st.text_area("Your text", value=default, height=180, placeholder="Paste a review or write a sentence...")
        analyze = st.button("Analyze sentiment  →", use_container_width=True)
    with right:
        st.markdown("### What you'll get")
        st.markdown("""
        <div class="panel">
          <div class="kicker">01 · Sentiment</div><p>Positive or negative prediction.</p>
          <div class="kicker">02 · Model score</div><p>A probability estimate from the selected classifier.</p>
          <div class="kicker">03 · Context</div><p>A short explanation of what the result means.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.caption("A machine-learning estimate, not a perfect understanding of language. Sarcasm, slang, and mixed opinions can be difficult.")

    if analyze:
        if not text_input.strip():
            st.warning("Please enter some text before analyzing.")
        else:
            label = int(model.predict([text_input.strip()])[0])
            if hasattr(model, "predict_proba"):
                scores = model.predict_proba([text_input.strip()])[0]
                confidence = float(scores[list(model.classes_).index(label)])
                positive_score = float(scores[list(model.classes_).index(1)])
            else:
                confidence, positive_score = None, None
            title = "Positive sentiment" if label == 1 else "Negative sentiment"
            css = "result-positive" if label == 1 else "result-negative"
            explanation = "The text is more likely to express a favorable opinion." if label == 1 else "The text is more likely to express an unfavorable opinion."
            st.markdown(f'<div class="{css}"><div class="kicker" style="color:inherit">MODEL PREDICTION</div><h2>{title}</h2><p style="margin:0;color:inherit">{explanation}</p></div>', unsafe_allow_html=True)
            if confidence is not None:
                st.write("")
                a, b = st.columns(2)
                a.metric("Predicted-class score", f"{confidence:.1%}")
                b.metric("Positive-class score", f"{positive_score:.1%}")
                st.progress(positive_score, text="Estimated positive sentiment")
            st.caption("Scores are model estimates and should not be interpreted as certainty.")

elif page == "Model insights":
    st.markdown('<div class="hero"><div class="eyebrow">MODEL REPORT · 02</div><h1>Inside the model.</h1><p>A quick look at the training data, held-out test results, and baseline model comparison.</p></div>', unsafe_allow_html=True)
    st.write("")
    ds = metrics["dataset"]
    bm = metrics["best_model_metrics"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Text examples", f'{ds["rows"]:,}')
    c2.metric("Test accuracy", f'{bm["accuracy"]:.1%}')
    c3.metric("Precision", f'{bm["precision"]:.1%}')
    c4.metric("F1-score", f'{bm["f1"]:.1%}')
    st.write("")
    st.markdown(f'**Selected model:** {metrics["best_model"]}  ·  **Training / test split:** {ds["train_rows"]:,} / {ds["test_rows"]:,}')
    st.markdown("### Model comparison")
    st.dataframe(metrics["model_comparison"], use_container_width=True, hide_index=True)
    image_path = ROOT / "reports" / "figures" / "confusion_matrix.png"
    if image_path.exists():
        st.markdown("### Where the model gets it right")
        st.image(str(image_path), caption="Confusion matrix on the held-out test set", width=560)
    st.caption("Results depend on this dataset and split. Performance on new domains or languages may differ.")

else:
    st.markdown('<div class="hero"><div class="eyebrow">PROJECT NOTES · 03</div><h1>Small data.<br>Useful signals.</h1><p>This project combines three labeled text files and trains classical machine-learning models to classify positive and negative sentiment.</p></div>', unsafe_allow_html=True)
    st.markdown("### How it works")
    st.markdown("""
    1. **Load:** Read the three tab-separated text files, each containing a sentence and a binary label.
    2. **Prepare:** Remove empty entries and duplicate text/label pairs, then create a stratified 80/20 train-test split.
    3. **Represent text:** TF-IDF converts words and two-word phrases into numeric features.
    4. **Compare:** Logistic Regression, Linear SVM, and Multinomial Naive Bayes are evaluated on the same held-out test set.
    5. **Predict:** The model with the highest test F1-score is saved and used by this application.
    """)
    st.markdown("### Dataset labels")
    st.markdown("- `0` → Negative sentiment\n- `1` → Positive sentiment")
    st.info("The source files contain 3,000 rows in total. After removing exact duplicate text/label pairs, the modeling dataset contains the rows reported in Model insights.")
