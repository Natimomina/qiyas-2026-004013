from datetime import date
from app import create_app, db
from app.models import Article, Entity
from app.nlp.entity_extractor import extract_entities
from app.nlp.sentiment import analyze_sentiment

app=create_app()

samples=[
    ('Abiy Ahmed discusses regional development in Gambella','Gambella Star','2025-04-10','Africa','The Prime Minister met regional officials to discuss development, peace, education and public services in Gambella. The meeting included federal and regional representatives.',),
    ('African Union and Ethiopia discuss regional cooperation','Gambella Star','2025-03-18','Africa','Officials from Ethiopia and the African Union discussed cooperation, economic growth, infrastructure and peace in East Africa.',),
    ('Health program expands in Gambella communities','GSN Agencies','2024-11-03','Health','A community health program expanded services in several Gambella locations, supporting families and improving access to preventive care.',),
]
with app.app_context():
    if Article.query.count():
        print('Demo data already exists.')
    else:
        for i,(title,author,dt,cat,text) in enumerate(samples,1):
            a=Article(title=title,author=author,publication_date=date.fromisoformat(dt),category=cat,subcategory=None,url=f'https://example.local/demo/{i}',article_text=text,summary=text,word_count=len(text.split()),character_count=len(text))
            a.sentiment_label,a.sentiment_score=analyze_sentiment(text)
            db.session.add(a); db.session.flush()
            for e in extract_entities(text):
                a.entities.append(Entity(entity_text=e['text'],entity_type=e['label'],start_position=e['start'],end_position=e['end']))
        db.session.commit(); print('Inserted 3 demo articles.')
