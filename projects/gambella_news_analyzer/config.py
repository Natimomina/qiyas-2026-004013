import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-change-me')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', f"sqlite:///{BASE_DIR / 'instance' / 'gambella_news.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    START_URL = os.getenv('START_URL', 'https://www.gambellastarnews.com/featured-articles')
    MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', '50'))
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '1.5'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '2'))
    TIMEOUT = int(os.getenv('TIMEOUT', '20'))
    USER_AGENT = os.getenv(
        'USER_AGENT',
        'GambellaNewsResearchBot/1.0 (+academic data collection; contact site owner before production crawling)'
    )
    MAX_DISCOVERY_PAGES = int(os.getenv('MAX_DISCOVERY_PAGES', '10'))
