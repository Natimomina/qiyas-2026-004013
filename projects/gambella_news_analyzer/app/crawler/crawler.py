import logging, threading, time
from collections import deque
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from flask import current_app
from .. import db
from ..models import Article, CrawlLog, Category
from .parser import extract_links, parse_article, is_candidate_article
from .robots import RobotsChecker

logger = logging.getLogger(__name__)

class CrawlManager:
    def __init__(self, app):
        self.app = app
        self.lock = threading.Lock()
        self.running = False
        self.stop_requested = False
        self.stats = {'discovered':0,'processed':0,'failed':0,'entities':0,'current_url':None,'status':'idle'}

    def start(self, max_articles=None, start_url=None, request_delay=None):
        with self.lock:
            if self.running:
                return False
            self.running = True; self.stop_requested = False
            self.stats = {'discovered':0,'processed':0,'failed':0,'entities':0,'current_url':None,'status':'starting'}
        t = threading.Thread(target=self._run, args=(max_articles, start_url, request_delay), daemon=True)
        t.start(); return True

    def stop(self): self.stop_requested = True

    def snapshot(self):
        with self.lock: return dict(self.stats)

    def _set(self, **kwargs):
        with self.lock: self.stats.update(kwargs)

    def _run(self, max_articles, start_url, request_delay):
        with self.app.app_context():
            try:
                cfg = current_app.config
                max_articles = max_articles or cfg['MAX_ARTICLES']
                start_url = start_url or cfg['START_URL']
                request_delay = request_delay if request_delay is not None else cfg['REQUEST_DELAY']
                user_agent = cfg['USER_AGENT']
                timeout = cfg['TIMEOUT']
                robots = RobotsChecker(start_url, user_agent, timeout)
                session = requests.Session(); session.headers.update({'User-Agent': user_agent})
                queue = deque([start_url]); seen=set(); page_count=0; article_urls=set()
                self._set(status='running')
                while queue and len(article_urls) < max_articles and page_count < cfg['MAX_DISCOVERY_PAGES'] and not self.stop_requested:
                    page_url = queue.popleft()
                    if page_url in seen: continue
                    seen.add(page_url); page_count += 1
                    if not robots.allowed(page_url):
                        db.session.add(CrawlLog(url=page_url,status='blocked',error_message='Disallowed by robots.txt'))
                        db.session.commit(); continue
                    self._set(current_url=page_url, discovered=len(article_urls))
                    try:
                        r = session.get(page_url, timeout=timeout)
                        db.session.add(CrawlLog(url=page_url,status='success' if r.ok else 'http_error',status_code=r.status_code))
                        db.session.commit()
                        if not r.ok: continue
                        soup = BeautifulSoup(r.text, 'html.parser')
                        links = extract_links(soup, page_url)
                        for u in links:
                            # Article heuristics: links with /<id>-<slug> or /category-like article paths.
                            if any(marker in u.lower() for marker in ['/featured-articles','?start=']) or u.rstrip('/') == start_url.rstrip('/'):
                                if u not in seen and u not in queue: queue.append(u)
                            else:
                                article_urls.add(u)
                                if len(article_urls) >= max_articles: break
                    except Exception as e:
                        logger.exception('Discovery failed: %s', page_url)
                        db.session.add(CrawlLog(url=page_url,status='failed',error_message=str(e))); db.session.commit()
                    time.sleep(request_delay)

                # Process discovered article URLs.
                for idx, article_url in enumerate(list(article_urls)[:max_articles], start=1):
                    if self.stop_requested: break
                    if not is_candidate_article(article_url) or not robots.allowed(article_url):
                        continue
                    self._set(current_url=article_url)
                    try:
                        existing = Article.query.filter_by(url=article_url).first()
                        if existing:
                            self._set(processed=idx)
                            time.sleep(request_delay); continue
                        r = session.get(article_url, timeout=timeout)
                        if not r.ok:
                            self._set(failed=self.stats['failed']+1); db.session.add(CrawlLog(url=article_url,status='http_error',status_code=r.status_code)); db.session.commit(); time.sleep(request_delay); continue
                        data = parse_article(r.text, article_url)
                        if not data.get('title') or data.get('word_count', 0) < 50:
                            db.session.add(CrawlLog(url=article_url,status='skipped',status_code=r.status_code,error_message='Page did not look like a substantive article'))
                            db.session.commit(); time.sleep(request_delay); continue
                        article = Article(**data)
                        db.session.add(article)
                        if data.get('category'):
                            cat = Category.query.filter_by(name=data['category']).first()
                            if not cat: db.session.add(Category(name=data['category']))
                        db.session.add(CrawlLog(url=article_url,status='success',status_code=r.status_code))
                        db.session.commit()
                        self._set(processed=self.stats['processed']+1)
                    except Exception as e:
                        logger.exception('Article failed: %s', article_url)
                        db.session.rollback(); db.session.add(CrawlLog(url=article_url,status='failed',error_message=str(e))); db.session.commit()
                        self._set(failed=self.stats['failed']+1)
                    time.sleep(request_delay)
                self._set(status='stopped' if self.stop_requested else 'completed', current_url=None)
            finally:
                with self.lock: self.running = False

crawl_manager = None

def get_manager(app):
    global crawl_manager
    if crawl_manager is None: crawl_manager = CrawlManager(app)
    return crawl_manager
