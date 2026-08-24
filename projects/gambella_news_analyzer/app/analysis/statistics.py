from sqlalchemy import func
from ..models import Article, Entity
from collections import Counter

def dashboard_stats():
    total = Article.query.count()
    entities = Entity.query.count()
    people = Entity.query.filter_by(entity_type='PERSON').count()
    orgs = Entity.query.filter_by(entity_type='ORG').count()
    locations = Entity.query.filter_by(entity_type='LOCATION').count()
    categories = Article.query.with_entities(Article.category, func.count(Article.id)).filter(Article.category.isnot(None)).group_by(Article.category).order_by(func.count(Article.id).desc()).all()
    months = Article.query.with_entities(func.strftime('%Y-%m', Article.publication_date), func.count(Article.id)).filter(Article.publication_date.isnot(None)).group_by(func.strftime('%Y-%m', Article.publication_date)).order_by(func.strftime('%Y-%m', Article.publication_date)).all()
    sentiments = Article.query.with_entities(Article.sentiment_label, func.count(Article.id)).group_by(Article.sentiment_label).all()
    return {
        'total_articles': total, 'total_entities': entities, 'people': people, 'organizations': orgs,
        'locations': locations, 'categories': [{'name':k or 'Unknown','count':v} for k,v in categories],
        'timeline': [{'period':k,'count':v} for k,v in months],
        'sentiment': [{'label':k or 'Unknown','count':v} for k,v in sentiments]
    }

def top_entities(limit=15, entity_type=None):
    q = Entity.query.with_entities(Entity.entity_text, Entity.entity_type, func.count(Entity.id).label('mentions'))
    if entity_type: q = q.filter_by(entity_type=entity_type)
    return [{'entity':e,'type':t,'mentions':m} for e,t,m in q.group_by(Entity.entity_text,Entity.entity_type).order_by(func.count(Entity.id).desc()).limit(limit).all()]
