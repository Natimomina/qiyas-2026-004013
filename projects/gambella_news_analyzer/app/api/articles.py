from flask import Blueprint, request, jsonify
from .. import db
from ..models import Article

articles_bp = Blueprint('articles_api', __name__)

def serialize(a, full=False):
    d={'id':a.id,'title':a.title,'author':a.author,'publication_date':a.publication_date.isoformat() if a.publication_date else None,'category':a.category,'subcategory':a.subcategory,'url':a.url,'word_count':a.word_count,'character_count':a.character_count,'sentiment_label':a.sentiment_label,'sentiment_score':a.sentiment_score}
    if full:
        d.update({'article_text':a.article_text,'summary':a.summary,'tags':a.tags,'image_url':a.image_url,'crawl_timestamp':a.crawl_timestamp.isoformat() if a.crawl_timestamp else None,'entities':[{'id':e.id,'text':e.entity_text,'type':e.entity_type,'start':e.start_position,'end':e.end_position} for e in a.entities]})
    return d

@articles_bp.get('')
def list_articles():
    q = Article.query
    search=request.args.get('search','').strip()
    category=request.args.get('category','').strip()
    author=request.args.get('author','').strip()
    entity_type=request.args.get('entity_type','').strip()
    if search: q=q.filter(Article.title.ilike(f'%{search}%') | Article.article_text.ilike(f'%{search}%'))
    if category: q=q.filter(Article.category==category)
    if author: q=q.filter(Article.author.ilike(f'%{author}%'))
    if entity_type:
        q=q.join(Article.entities).filter_by(entity_type=entity_type).distinct()
    page=max(int(request.args.get('page',1)),1); limit=min(max(int(request.args.get('limit',20)),1),100)
    pagination=q.order_by(Article.publication_date.desc(),Article.id.desc()).paginate(page=page,per_page=limit,error_out=False)
    return jsonify({'items':[serialize(a) for a in pagination.items],'page':page,'limit':limit,'total':pagination.total,'pages':pagination.pages})

@articles_bp.get('/<int:article_id>')
def article_detail(article_id):
    a=Article.query.get_or_404(article_id)
    return jsonify(serialize(a, True))
