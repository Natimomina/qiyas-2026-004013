from flask import Blueprint, render_template, send_from_directory
from pathlib import Path

main_bp=Blueprint('main',__name__)

@main_bp.get('/')
def dashboard(): return render_template('dashboard.html')
@main_bp.get('/articles')
def articles_page(): return render_template('articles.html')
@main_bp.get('/articles/<int:article_id>')
def article_page(article_id): return render_template('article_detail.html', article_id=article_id)
@main_bp.get('/entities')
def entities_page(): return render_template('entities.html')
@main_bp.get('/crawl')
def crawl_page(): return render_template('crawl_manager.html')
@main_bp.get('/export/<kind>')
def export_page(kind):
    # Implemented client-side via JSON API for simplicity.
    return {'message':f'Use the Export buttons in the dashboard for {kind} data.'}
