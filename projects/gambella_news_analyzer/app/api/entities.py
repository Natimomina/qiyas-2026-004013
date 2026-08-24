from flask import Blueprint, request, jsonify
from sqlalchemy import func
from ..models import Entity, Article
from ..analysis.relationships import article_relationships

entities_bp=Blueprint('entities_api',__name__)

@entities_bp.get('')
def list_entities():
    entity_type=request.args.get('type')
    limit=min(max(int(request.args.get('limit',100)),1),500)
    q=Entity.query.with_entities(Entity.entity_text,Entity.entity_type,func.count(Entity.id).label('mentions'))
    if entity_type: q=q.filter(Entity.entity_type==entity_type)
    rows=q.group_by(Entity.entity_text,Entity.entity_type).order_by(func.count(Entity.id).desc()).limit(limit).all()
    return jsonify([{'entity':e,'type':t,'mentions':m} for e,t,m in rows])

@entities_bp.get('/<path:entity_text>')
def entity_articles(entity_text):
    rows=Entity.query.filter(Entity.entity_text.ilike(entity_text)).all()
    return jsonify({'entity':entity_text,'articles':[{'id':e.article.id,'title':e.article.title,'url':e.article.url} for e in rows]})

@entities_bp.get('/article/<int:article_id>/relationships')
def relationships(article_id):
    a=Article.query.get_or_404(article_id)
    return jsonify(article_relationships(a))
