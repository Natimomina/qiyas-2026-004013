from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config


db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    CORS(app)

    from .routes import main_bp
    from .api.articles import articles_bp
    from .api.entities import entities_bp
    from .api.statistics import statistics_bp
    from .api.crawler import crawler_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(articles_bp, url_prefix='/api/articles')
    app.register_blueprint(entities_bp, url_prefix='/api/entities')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    app.register_blueprint(crawler_bp, url_prefix='/api/crawl')

    with app.app_context():
        from . import models
        db.create_all()

    return app
