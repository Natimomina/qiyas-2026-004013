# 🎬 MovieIQ --- Movie Intelligence & Recommendation Platform

> An end-to-end data science and machine learning project that turns
> movie data into an interactive recommendation and prediction platform.

## 📌 Overview

**MovieIQ** is an end-to-end movie intelligence platform built around
approximately **4,000 movie records**.

The project takes the workflow beyond notebooks by connecting data
cleaning, exploratory analysis, machine learning, recommendation
systems, and a Flask web application.

Users can:

-   Search for movies
-   Discover similar movies
-   Predict audience scores
-   Estimate gross revenue
-   Classify whether a movie reaches the project's high-score threshold
-   Explore movie information through a modern web interface

``` text
Movie Dataset
     ↓
Data Cleaning
     ↓
Exploratory Data Analysis
     ↓
Movie Industry Analysis
     ↓
Machine Learning
     ↓
Recommendation System
     ↓
Flask Backend
     ↓
Interactive MovieIQ UI
```

------------------------------------------------------------------------

## 🎯 Why I Built This

I built MovieIQ to practice turning data science work into a usable
product.

Rather than stopping after analysis and model training, the project
connects the full workflow:

-   Data preparation
-   Statistical exploration
-   Machine learning
-   Recommendation systems
-   Backend development
-   Front-end development

The project demonstrates practical skills across **Data Analytics,
Machine Learning, and Applied AI**.

------------------------------------------------------------------------

# ✨ Key Features

## 🔎 Movie Search

Search the movie dataset by title and view key information including:

-   Title
-   Genre
-   Year
-   Runtime
-   Director
-   Country
-   Audience score

## 🎬 Content-Based Recommendations

MovieIQ recommends similar movies using movie metadata such as:

-   Genre
-   Director
-   Writer
-   Star
-   Country
-   Production company
-   Rating

The recommendation engine uses **TF-IDF** and **cosine similarity**.

## ⭐ Rating Prediction

A regression model estimates audience score from:

-   Year
-   Runtime
-   Genre
-   MPAA rating
-   Country
-   Release month

## 💰 Revenue Prediction

A regression model estimates gross revenue.

Because gross revenue is strongly right-skewed, the target is
transformed using `log1p()` during training and converted back with
`expm1()` for display.

> This is an experimental machine-learning model, not a financial
> forecasting tool.

## 🎯 Success Classification

The project defines success as an audience score of **7.0 or higher**.

``` text
score >= 7.0 → High audience-score class
score < 7.0  → Below threshold
```

This definition refers to audience-score performance, not commercial
success.

------------------------------------------------------------------------

# 🤖 Machine Learning

MovieIQ contains three prediction models.

  -----------------------------------------------------------------------
  Model             Problem           Target            Main Approach
  ----------------- ----------------- ----------------- -----------------
  Rating Predictor  Regression        `score`           Random Forest

  Revenue Predictor Regression        `gross`           Log-transformed
                                                        Random Forest

  Success           Classification    `score >= 7.0`    Random Forest
  Classifier                                            
  -----------------------------------------------------------------------

### Rating Prediction

The rating pipeline includes:

-   Train/test split
-   Numerical imputation
-   Categorical imputation
-   One-hot encoding
-   Random Forest regression
-   MAE
-   RMSE
-   R²

### Revenue Prediction

The revenue model uses features including:

-   Year
-   Score
-   Votes
-   Budget
-   Runtime
-   Genre
-   Rating
-   Country
-   Release information

The target is log-transformed before training.

### Success Classification

The classifier excludes the target score itself to avoid target leakage.

Evaluation includes:

-   Accuracy
-   Precision
-   Recall
-   F1-score
-   ROC-AUC
-   Confusion matrix

------------------------------------------------------------------------

# 🎥 Recommendation System

MovieIQ uses a **content-based recommendation system**.

### How it works

**1. Combine movie metadata**

``` text
Genre + Director + Writer + Star + Country + Company + Rating
```

**2. Convert text into numerical vectors**

The project uses **TF-IDF (Term Frequency--Inverse Document
Frequency)**.

**3. Measure similarity**

Movies are compared using **cosine similarity**.

**4. Return similar movies**

The highest-similarity movies are returned as recommendations.

``` text
User selects movie
       ↓
Find movie
       ↓
TF-IDF representation
       ↓
Cosine similarity
       ↓
Sort similar movies
       ↓
Return recommendations
```

------------------------------------------------------------------------

# 📊 Data Analysis

The project contains a complete notebook-based analytical workflow.

### Data Inspection

Examines:

-   Dataset shape
-   Data types
-   Missing values
-   Duplicate records
-   Data quality issues

### Data Cleaning

Handles:

-   Runtime formatting
-   Release-date parsing
-   Missing values
-   Numeric conversion
-   Budget and gross handling
-   Release year extraction
-   Release month extraction
-   Text cleanup

The cleaned dataset contains approximately **4,000 records and 18
columns**.

### Exploratory Data Analysis

The EDA covers:

-   Movies by year
-   Average score by year
-   Genre distribution
-   Genre scores
-   Runtime distribution
-   Runtime vs. score
-   Budget
-   Gross revenue
-   Profit
-   ROI
-   Votes vs. score
-   Correlations
-   Release months
-   Directors
-   Production companies

### Movie Industry Analysis

The industry-analysis notebook examines patterns in:

-   Genre performance
-   Financial performance
-   Gross revenue
-   Profit
-   ROI
-   Scores
-   Production companies
-   Directors
-   Release timing

> These findings describe patterns within this dataset and should not
> automatically be interpreted as universal movie-industry facts.

------------------------------------------------------------------------

# 🧰 Tech Stack

### Programming

-   Python

### Data Analysis

-   Pandas
-   NumPy
-   Matplotlib
-   Seaborn

### Machine Learning

-   Scikit-learn
-   Random Forest
-   TF-IDF
-   Cosine Similarity

### Web Application

-   Flask
-   HTML
-   CSS
-   JavaScript

### Model Storage

-   Joblib
-   SciPy sparse matrices

### Development

-   Jupyter Notebook
-   VS Code
-   Git
-   GitHub

------------------------------------------------------------------------

# 🏗️ Project Architecture

``` text
                    ┌───────────────────┐
                    │   Movie Dataset   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Data Preparation  │
                    └─────────┬─────────┘
                              │
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
       Data Analysis      ML Training      Recommendation
             │                │                │
             │       ┌────────┼────────┐       │
             │       ▼        ▼        ▼       │
             │    Rating   Revenue   Success   │
             │     Model     Model    Model    │
             │       └────────┼────────┘       │
             │                │                │
             └────────────────┼────────────────┘
                              ▼
                    ┌───────────────────┐
                    │  Flask Backend    │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    MovieIQ UI     │
                    └───────────────────┘
```

------------------------------------------------------------------------

# 🖥️ Screenshots

Add application screenshots to the `screenshots/` folder as the UI
evolves.

Recommended screenshots:

``` text
screenshots/
├── dashboard.png
├── recommendations.png
└── predictions.png
```

Then display them in this section:

``` markdown
![MovieIQ Dashboard](screenshots/dashboard.png)
```

------------------------------------------------------------------------

# ⚙️ Installation

## 1. Clone the repository

``` bash
git clone <your-repository-url>
cd movie-intelligence-platform
```

## 2. Create a virtual environment

### Windows

``` bash
python -m venv .venv
.venv\Scriptsctivate
```

### macOS / Linux

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

``` bash
pip install -r requirements.txt
```

The project pins the Scikit-learn version used by the serialized models
to reduce model-loading compatibility problems.

## 4. Verify the model files

The `models/` directory should contain:

``` text
models/
├── rating_model.pkl
├── revenue_model.pkl
├── success_classifier.pkl
├── movie_tfidf_vectorizer.pkl
├── movie_tfidf_matrix.npz
├── movie_title_index.pkl
└── movie_recommendation_data.csv
```

------------------------------------------------------------------------

# ▶️ Usage

Start the Flask application:

``` bash
python app/app.py
```

Open the local Flask address in your browser, normally:

``` text
http://127.0.0.1:5000
```

From there you can search for movies, generate recommendations, and open
the prediction tools.

------------------------------------------------------------------------

# 📁 Project Structure

``` text
movie-intelligence-platform/
│
├── app/
│   ├── app.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── app.js
│       └── styles.css
│
├── data/
│
├── models/
│   ├── rating_model.pkl
│   ├── revenue_model.pkl
│   ├── success_classifier.pkl
│   ├── movie_tfidf_vectorizer.pkl
│   ├── movie_tfidf_matrix.npz
│   ├── movie_title_index.pkl
│   └── movie_recommendation_data.csv
│
├── notebooks/
│   ├── 01_data_inspection.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_exploratory_data_analysis.ipynb
│   ├── 04_movie_industry_analysis.ipynb
│   ├── 05_rating_prediction.ipynb
│   ├── 06_revenue_prediction.ipynb
│   ├── 07_success_classification.ipynb
│   └── 08_movie_recommendation.ipynb
│
├── screenshots/
├── .gitignore
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

# ⚠️ Model Limitations

### Dataset limitations

The dataset contains missing values, particularly in financial fields
such as budget and gross revenue.

Some categories contain relatively few records, so results for very
small groups should be interpreted carefully.

### Rating prediction

The rating model learns patterns from the available dataset. Predictions
should not be treated as guaranteed future audience scores.

### Revenue prediction

Movie revenue depends on many real-world factors that are not
represented in the dataset.

The model should therefore be treated as an experimental prediction
system rather than a financial forecast.

### Success classification

The project's success target is:

``` text
score >= 7.0
```

Therefore, the classifier predicts high audience-score performance
rather than commercial success.

### Recommendation system

Recommendations are based on metadata similarity. Similarity does not
guarantee that a user will enjoy a recommended movie.

------------------------------------------------------------------------

# 🚀 Future Improvements

-   [ ] Interactive movie analytics dashboard
-   [ ] Movie detail pages
-   [ ] Genre, country, and year filters
-   [ ] Interactive charts
-   [ ] Richer recommendation cards
-   [ ] Recommendation explanations
-   [ ] Model performance dashboard
-   [ ] Prediction explanations
-   [ ] User preference-based recommendations
-   [ ] More advanced recommendation techniques
-   [ ] Improved UI animations and transitions
-   [ ] API documentation
-   [ ] Automated tests
-   [ ] Docker support
-   [ ] Production deployment

------------------------------------------------------------------------

# 📚 Notebooks

The project follows a structured notebook workflow:

``` text
01 → Data Inspection
02 → Data Cleaning
03 → Exploratory Data Analysis
04 → Movie Industry Analysis
05 → Rating Prediction
06 → Revenue Prediction
07 → Success Classification
08 → Movie Recommendation
```

This makes it possible to follow the project from the original dataset
through analysis and model development to the final web application.

------------------------------------------------------------------------

# 🧠 What This Project Demonstrates

MovieIQ brings together practical skills in:

-   Data cleaning
-   Exploratory data analysis
-   Data visualization
-   Feature engineering
-   Regression
-   Classification
-   Model evaluation
-   Text vectorization
-   Similarity search
-   Recommendation systems
-   Model serialization
-   Flask API development
-   Front-end development
-   Git/GitHub workflow
-   Turning ML notebooks into a usable application

------------------------------------------------------------------------

# 👤 Author

**Natnael Tesfaye Mekonen**

GitHub: [Natimomina](https://github.com/Natimomina)

------------------------------------------------------------------------

## ⭐ Project

MovieIQ represents the complete path from **data to intelligence to
product**.
