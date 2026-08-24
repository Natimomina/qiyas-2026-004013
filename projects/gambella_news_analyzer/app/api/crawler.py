from flask import Blueprint, jsonify, request, current_app
from ..crawler.crawler import get_manager
from .. import db
from ..models import Article
from ..nlp.entity_extractor import extract_entities
from ..nlp.sentiment import analyze_sentiment

crawler_bp=Blueprint('crawler_api',__name__)

def process_nlp_batch():
    count=0; entity_count=0
    for article in Article.query.all():
        article.entities.clear()
        ents=extract_entities(article.article_text or '')
        for e in ents:
            from ..models import Entity
            article.entities.append(Entity(entity_text=e['text'],entity_type=e['label'],start_position=e['start'],end_position=e['end']))
        article.sentiment_label,article.sentiment_score=analyze_sentiment(article.article_text or '')
        entity_count += len(ents); count += 1
    db.session.commit()
    return count,entity_count

@crawler_bp.post('/start')
def start():
    payload=request.get_json(silent=True) or {}
    manager=get_manager(current_app._get_current_object())
    ok=manager.start(payload.get('max_articles'),payload.get('start_url'),payload.get('request_delay'))
    return jsonify({'started':ok,'status':manager.snapshot()}), (202 if ok else 409)

@crawler_bp.post('/stop')
def stop():
    manager=get_manager(current_app._get_current_object()); manager.stop(); return jsonify(manager.snapshot())

@crawler_bp.get('/status')
def status(): return jsonify(get_manager(current_app._get_current_object()).snapshot())

@crawler_bp.post('/process-nlp')
def process_nlp():
    count,entities=process_nlp_batch()
    return jsonify({'articles_processed':count,'entities_created':entities})

@crawler_bp.get('/logs')
def logs():
    from ..models import CrawlLog
    rows=CrawlLog.query.order_by(CrawlLog.id.desc()).limit(100).all()
    return jsonify([{'url':r.url,'status':r.status,'status_code':r.status_code,'error':r.error_message,'timestamp':r.crawl_timestamp.isoformat() if r.crawl_timestamp else None} for r in rows])
