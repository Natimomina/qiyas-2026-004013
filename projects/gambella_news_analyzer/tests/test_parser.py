from app.crawler.parser import parse_article, canonicalize

def test_canonicalize():
    assert canonicalize('/world/test', 'https://www.gambellastarnews.com/') == 'https://www.gambellastarnews.com/world/test'
    assert canonicalize('https://example.com/a', 'https://www.gambellastarnews.com/') is None

def test_parse_article():
    html='''<html><head><meta name="description" content="Test summary"></head><body><h1>Test article</h1><div class="article-body"><p>April 10, 2025 (GSN) - This is a test article with enough content to be parsed correctly by the parser. It contains several words and details.</p></div></body></html>'''
    d=parse_article(html,'https://www.gambellastarnews.com/africa/test-article')
    assert d['title']=='Test article'
    assert d['publication_date'].year==2025
    assert d['word_count']>10
