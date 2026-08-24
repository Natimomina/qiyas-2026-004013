# Gambella Star News Analytics

A Flask + SQLite research application for crawling publicly accessible Gambella Star News pages, storing article metadata/text, extracting NLP entities, calculating statistics, and exploring the results in a dashboard.

## Features

- Respectful, configurable crawling with `robots.txt` checks and delay.
- Article extraction: title, author, publication date, category, subcategory, URL, body, summary, tags, image URL, word/character counts.
- SQLite database through SQLAlchemy.
- NLP entity extraction for PERSON, ORG, LOCATION, DATE, MONEY and EVENT when spaCy's English model is installed.
- Lightweight sentiment estimate as an optional analysis signal.
- Dashboard, article search, entity explorer, crawl manager and client-side CSV exports.
- REST APIs.

## Installation on Windows / Anaconda

```bash
conda create -n gsn-analytics python=3.11 -y
conda activate gsn-analytics
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python run.py
```

Open: `http://127.0.0.1:5000`

## First run

1. Open **Crawl Manager**.
2. Set a small limit such as 10–20 articles.
3. Keep a conservative delay (for example 1.5–3 seconds).
4. Start the crawl.
5. After it finishes, click **Run NLP Processing**.
6. Open the dashboard and entity explorer.

## Configuration

Copy `.env.example` to `.env` and adjust values as needed. The app reads environment variables through the Flask configuration if you load them in your shell/process manager.

## Important crawling guidance

Use only publicly accessible pages, respect `robots.txt`, terms of use, rate limits, and applicable laws. Do not bypass authentication, CAPTCHAs, paywalls, or technical controls. Keep the request rate low and use a small crawl limit while developing.

The parser intentionally uses multiple selector fallbacks because article pages may not all have identical HTML. Real-world sites change, so selectors may need maintenance over time.

## Architecture

```text
Gambella Star News
        |
        v
   Crawler + Parser
        |
        v
      SQLite
        |
        +----> NLP Entity Extraction
        |
        +----> Sentiment Estimate
        |
        v
     Flask API
        |
        v
  Bootstrap + Chart.js UI
```

## Notes

The crawler is intentionally conservative. It is not designed to mirror an entire site indefinitely. It is a portfolio/academic data-collection system and should be run in small batches.
