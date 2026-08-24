from datetime import datetime
from . import db

class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(255))
    publication_date = db.Column(db.Date)
    category = db.Column(db.String(150))
    subcategory = db.Column(db.String(150))
    url = db.Column(db.Text, unique=True, nullable=False, index=True)
    article_text = db.Column(db.Text)
    summary = db.Column(db.Text)
    tags = db.Column(db.Text)
    image_url = db.Column(db.Text)
    word_count = db.Column(db.Integer, default=0)
    character_count = db.Column(db.Integer, default=0)
    crawl_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sentiment_label = db.Column(db.String(32))
    sentiment_score = db.Column(db.Float)
    entities = db.relationship('Entity', backref='article', lazy=True, cascade='all, delete-orphan')

class Entity(db.Model):
    __tablename__ = 'entities'
    id = db.Column(db.Integer, primary_key=True)
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False, index=True)
    entity_text = db.Column(db.String(500), nullable=False, index=True)
    entity_type = db.Column(db.String(32), nullable=False, index=True)
    start_position = db.Column(db.Integer)
    end_position = db.Column(db.Integer)

class CrawlLog(db.Model):
    __tablename__ = 'crawl_logs'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(32), nullable=False)
    status_code = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    crawl_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    url = db.Column(db.Text)
