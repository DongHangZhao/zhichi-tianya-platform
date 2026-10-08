'''
Author: your name
Date: 2026-03-15 02:10:19
LastEditTime: 2026-03-15 02:10:19
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\routes\news.py
'''
"""
新闻相关路由
"""

import calendar
from models import db, News
from datetime import datetime, timedelta, date as date_obj
from flask import Blueprint, render_template, request, flash, redirect, url_for

news_bp = Blueprint('news_routes', __name__)


@news_bp.route('/calendar')
def news_calendar():
    """新闻日历视图"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)

    first_day = date_obj(year, month, 1)
    if month == 12:
        last_day = date_obj(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date_obj(year, month + 1, 1) - timedelta(days=1)

    monthly_news = News.query.filter(
        News.timestamp >= first_day,
        News.timestamp <= last_day
    ).order_by(News.timestamp.desc()).all()

    news_by_date = {}
    for news in monthly_news:
        date_key = news.timestamp.date()
        if date_key not in news_by_date:
            news_by_date[date_key] = []
        news_by_date[date_key].append(news)

    cal = calendar.monthcalendar(year, month)

    day_info = {}
    for week in cal:
        for day in week:
            if day != 0:
                current_date = date_obj(year, month, day)
                is_weekend = calendar.weekday(year, month, day) >= 5
                day_info[day] = {
                    'date': current_date,
                    'is_weekend': is_weekend,
                    'has_news': current_date in news_by_date
                }

    return render_template('news_calendar.html',
                           year=year,
                           month=month,
                           calendar_days=cal,
                           news_by_date=news_by_date,
                           day_info=day_info,
                           date=date_obj)


@news_bp.route('/date/<date_str>')
def news_by_date(date_str):
    """按日期查看新闻"""
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_news = News.query.filter(
            db.func.date(News.timestamp) == target_date
        ).order_by(News.timestamp.desc()).all()

        return render_template('news_by_date.html',
                               target_date=target_date,
                               news_items=day_news)
    except Exception as e:
        flash(f'日期格式错误：{str(e)}', 'danger')
        return redirect(url_for('news'))


@news_bp.route('/search')
def news_search():
    """新闻搜索（支持关键字和日期）"""
    keyword = request.args.get('keyword', '')
    search_date = request.args.get('date', '')
    source = request.args.get('source', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = News.query

    if keyword:
        query = query.filter(
            db.or_(
                News.title.ilike(f'%{keyword}%'),
                News.content.ilike(f'%{keyword}%'),
                News.summary.ilike(f'%{keyword}%')
            )
        )

    if source:
        query = query.filter(News.source == source)

    if search_date:
        try:
            target_date = datetime.strptime(search_date, '%Y-%m-%d').date()
            query = query.filter(
                db.func.date(News.timestamp) == target_date
            )
        except:
            pass

    pagination = query.order_by(News.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    news_items = pagination.items

    sources = db.session.query(News.source).distinct().all()
    sources = [s[0] for s in sources]

    return render_template('news_search.html',
                           news_items=news_items,
                           pagination=pagination,
                           keyword=keyword,
                           search_date=search_date,
                           selected_source=source,
                           sources=sources)
