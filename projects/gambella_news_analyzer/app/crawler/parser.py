import json
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

BASE_DOMAIN = 'gambellastarnews.com'


def clean_text(text):
    return re.sub(r'\s+', ' ', text or '').strip()


def canonicalize(url, base_url):
    absolute = urljoin(base_url, url)
    p = urlparse(absolute)
    if p.scheme not in {'http', 'https'}:
        return None
    if p.netloc.lower().lstrip('www.') != BASE_DOMAIN:
        return None
    return absolute.split('#')[0]


def is_candidate_article(url):
    if not url or not url.startswith(('http://', 'https://')):
        return False
    p = urlparse(url)
    if p.netloc.lower().lstrip('www.') != BASE_DOMAIN:
        return False
    path = p.path.lower().rstrip('/')
    excluded = ['/category/', '/tag/', '/author/', '/contact', '/about', '/privacy', '/terms']
    if any(x in path for x in excluded):
        return False
    parts = [x for x in path.split('/') if x]
    # GSN article URLs typically include a numeric Joomla-style section/article id.
    return len(parts) >= 2 and any(any(ch.isdigit() for ch in part) for part in parts[1:])


def extract_links(soup, base_url):
    links = set()
    for a in soup.find_all('a', href=True):
        u = canonicalize(a['href'], base_url)
        if u and is_candidate_article(u):
            links.add(u)
    return links


def parse_date(value):
    if not value:
        return None
    value = clean_text(value)
    candidates = [value]
    for fmt in ['%d %B %Y','%B %d, %Y','%d %b %Y','%b %d, %Y','%Y-%m-%d','%Y/%m/%d']:
        for c in candidates:
            try:
                return datetime.strptime(c, fmt).date()
            except ValueError:
                pass
    m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', value)
    if m:
        try: return datetime.strptime(m.group(0), '%d %B %Y').date()
        except ValueError: pass
    return None


def _meta(soup, names):
    for name in names:
        el = soup.find('meta', attrs={'name': name}) or soup.find('meta', attrs={'property': name})
        if el and el.get('content'):
            return clean_text(el['content'])
    return None


def parse_article(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    for tag in soup(['script','style','noscript','nav','footer','header','aside','form']):
        tag.decompose()

    title = None
    for sel in ['h1', '.page-header h2', '.item-title', '.article-title']:
        el = soup.select_one(sel)
        if el and clean_text(el.get_text(' ')):
            title = clean_text(el.get_text(' ')); break
    if not title:
        title = _meta(soup, ['og:title','twitter:title']) or (clean_text(soup.title.get_text()) if soup.title else '')

    author = _meta(soup, ['author','article:author'])
    if not author:
        for sel in ['.createdby','.author','.item-author','.article-info']:
            el = soup.select_one(sel)
            if el:
                txt = clean_text(el.get_text(' '))
                m = re.search(r'(?:By|Author)\s*[:\-]?\s*(.+)', txt, re.I)
                if m: author = clean_text(m.group(1)); break
                if len(txt) < 120: author = txt

    date_raw = _meta(soup, ['article:published_time','date','publish_date','dc.date'])
    if not date_raw:
        for sel in ['time','.published','.createdate','.item-date','.article-info']:
            el = soup.select_one(sel)
            if el:
                date_raw = el.get('datetime') or clean_text(el.get_text(' '));
                if date_raw: break
    publication_date = parse_date(date_raw)

    category = None
    crumbs = soup.select('.breadcrumb a, .breadcrumb li, .category-name, .item-category')
    if crumbs:
        vals = [clean_text(x.get_text(' ')) for x in crumbs if clean_text(x.get_text(' '))]
        vals = [v for v in vals if v.lower() not in {'home','featured articles','details'}]
        if vals: category = vals[-1]

    if not category:
        path = urlparse(url).path.strip('/').split('/')
        if path and path[0] in {'africa','world','technology','sport','education','health','travel','community','opinion','editorial'}:
            category = path[0].title()

    subcategory = None
    if category and crumbs:
        vals = [clean_text(x.get_text(' ')) for x in crumbs if clean_text(x.get_text(' '))]
        vals = [v for v in vals if v.lower() not in {'home','featured articles','details'}]
        if len(vals) >= 2: subcategory = vals[-1]

    summary = _meta(soup, ['description','og:description','twitter:description'])
    image_url = _meta(soup, ['og:image','twitter:image'])

    article_root = None
    selectors = ['.item-page','.blog-item','.article-body','.entry-content','article','.single-article','.main-content']
    for sel in selectors:
        el = soup.select_one(sel)
        if el and len(clean_text(el.get_text(' '))) > 200:
            article_root = el; break
    if article_root is None:
        article_root = soup.body or soup

    paragraphs = [clean_text(p.get_text(' ')) for p in article_root.find_all(['p','h2','h3'])]
    paragraphs = [p for p in paragraphs if len(p) > 20]
    text = '\n'.join(paragraphs)
    if not text or len(text) < 100:
        text = clean_text(article_root.get_text(' '))

    tags = []
    for el in soup.select('.tags a, .tagspopular a'):
        t = clean_text(el.get_text(' '))
        if t: tags.append(t)
    if not tags:
        kw = _meta(soup, ['keywords'])
        if kw: tags = [x.strip() for x in kw.split(',') if x.strip()]

    if image_url: image_url = urljoin(url, image_url)

    return {
        'title': title or 'Untitled',
        'author': author,
        'publication_date': publication_date,
        'category': category,
        'subcategory': subcategory,
        'url': url,
        'article_text': text,
        'summary': summary,
        'tags': json.dumps(tags, ensure_ascii=False),
        'image_url': image_url,
        'word_count': len(text.split()),
        'character_count': len(text),
    }
