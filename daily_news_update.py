'''
Author: your name
Date: 2026-04-11 22:00:46
LastEditTime: 2026-04-11 22:00:47
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\daily_news_update.py
'''
"""
每日新闻自动更新脚本
应用启动时自动执行，采集当天真实新闻
"""

import sys
import os
import random
import time
from datetime import datetime
from app import app, db
from scrape_the_paper import scrape_the_paper_news
from models import News

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def collect_daily_news():
    """采集当天新闻"""

    today = datetime.now().strftime('%Y-%m-%d')

    print("\n" + "="*70)
    print(f"每日新闻自动更新 - {today}")
    print("="*70)

    total_saved = 0
    total_duplicate = 0

    with app.app_context():
        # 检查今天是否已有新闻
        today_count = News.query.filter(
            db.func.date(News.timestamp) == datetime.now().date()
        ).count()

        if today_count > 50:
            print(f"✅ 今天已有 {today_count} 条新闻，跳过采集")
            return 0, 0

        print(f"今天已有 {today_count} 条新闻，开始采集...")

        # 1. 澎湃新闻
        try:
            print("\n[1/3] 澎湃新闻采集...")
            saved, dup = scrape_the_paper_news()
            total_saved += saved
            total_duplicate += dup
            time.sleep(2)
        except Exception as e:
            print(f"✗ 澎湃新闻失败: {e}")

        # 2. 从scrape_news.py采集
        try:
            print("\n[2/3] 综合新闻采集...")
            from scrape_news import scrape_domestic_news

            news_data = scrape_domestic_news()

            if news_data:
                for news_item in news_data:
                    existing = News.query.filter_by(
                        title=news_item['title']).first()
                    if existing:
                        total_duplicate += 1
                        continue

                    news = News(
                        title=news_item['title'],
                        content=news_item['content'],
                        summary=news_item['summary'],
                        image_url=news_item.get('image_url', ''),
                        source=news_item['source'],
                        url='',
                        timestamp=datetime.now(),
                        views=random.randint(100, 5000)
                    )
                    db.session.add(news)
                    total_saved += 1

                try:
                    db.session.commit()
                    print(f"  ✓ 保存 {len(news_data)} 条")
                except Exception as e:
                    print(f"  ✗ 保存失败: {e}")
                    db.session.rollback()

            time.sleep(2)
        except Exception as e:
            print(f"✗ 综合采集失败: {e}")

        # 3. 真实新闻爬虫（如果可用）
        try:
            print("\n[3/3] 多源新闻采集...")
            from real_news_scraper import RealNewsScraper

            scraper = RealNewsScraper()
            news_list = scraper.scrape_real_news()

            if news_list:
                saved, dup = scraper.save_news_to_db(news_list)
                total_saved += saved
                total_duplicate += dup
        except Exception as e:
            print(f"✗ 多源采集失败: {e}")

        # 统计
        total_news = News.query.count()
        today_final = News.query.filter(
            db.func.date(News.timestamp) == datetime.now().date()
        ).count()

        print(f"\n{'='*70}")
        print(f"✅ 今日采集完成")
        print(f"新增: {total_saved} 条")
        print(f"重复: {total_duplicate} 条")
        print(f"今天总计: {today_final} 条")
        print(f"数据库总量: {total_news} 条")
        print(f"{'='*70}")

        return total_saved, total_duplicate


def auto_update_on_startup():
    """应用启动时自动更新"""

    import threading

    def update_background():
        """后台执行"""
        try:
            with app.app_context():
                collect_daily_news()
        except Exception as e:
            print(f"\n[自动更新] 失败: {e}")

    # 在后台线程执行
    t = threading.Thread(target=update_background, daemon=True)
    t.start()


if __name__ == '__main__':
    collect_daily_news()
