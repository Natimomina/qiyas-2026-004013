from flask import Blueprint, jsonify, request
from ..analysis.statistics import dashboard_stats, top_entities
from ..models import Article
from sqlalchemy import func

statistics_bp=Blueprint('statistics_api',__name__)

@statistics_bp.get('')
def stats(): return jsonify(dashboard_stats())

@statistics_bp.get('/top')
def top(): return jsonify(top_entities(int(request.args.get('limit',15)), request.args.get('type')))

@statistics_bp.get('/gambella')
def gambella():
    q=Article.query.filter((Article.article_text.ilike('%Gambella%')) | (Article.title.ilike('%Gambella%')))
    return jsonify({'total':q.count()})
