'''
Author: your name
Date: 2026-04-10 20:33:33
LastEditTime: 2026-04-10 20:33:33
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\verify_news.py
'''
"""验证新闻数据"""
from app import app, db
from models import News

with app.app_context():
    total = News.query.count()
    print(f'新闻总数: {total}')

    earliest = News.query.order_by(News.timestamp.asc()).first()
    latest = News.query.order_by(News.timestamp.desc()).first()

    print(f'\n最早新闻:')
    print(
        f'  时间: {earliest.timestamp.strftime("%Y-%m-%d %H:%M") if earliest else "无"}')
    print(f'  标题: {earliest.title if earliest else "无"}')
    print(f'  来源: {earliest.source if earliest else "无"}')

    print(f'\n最新新闻:')
    print(
        f'  时间: {latest.timestamp.strftime("%Y-%m-%d %H:%M") if latest else "无"}')
    print(f'  标题: {latest.title if latest else "无"}')
    print(f'  来源: {latest.source if latest else "无"}')

    # 按月份统计
    print('\n按月份统计:')
    from sqlalchemy import extract, func
    monthly_stats = db.session.query(
        extract('year', News.timestamp).label('year'),
        extract('month', News.timestamp).label('month'),
        func.count(News.id).label('count')
    ).group_by('year', 'month').order_by('year', 'month').all()

    for year, month, count in monthly_stats:
        print(f'  {int(year)}年{int(month)}月: {count} 条')
