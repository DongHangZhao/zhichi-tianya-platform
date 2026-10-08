'''
Author: your name
Date: 2026-04-11 22:16:16
LastEditTime: 2026-04-11 22:16:16
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\final_news_update.py
'''
"""
最终版每日新闻更新
- 澎湃新闻真实爬虫（链接已验证）
- 应用启动自动执行
- 自动去重
"""

import sys
import os
import threading
import time
from datetime import datetime
from app import app, db
from scrape_thepaper_real import scrape_and_save as scrape_thepaper
from models import News

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def daily_news_update():
    """每日新闻更新"""

    today = datetime.now().strftime('%Y-%m-%d')

    print("\n" + "="*70)
    print(f"每日新闻自动更新 - {today}")
    print("="*70)

    with app.app_context():
        # 检查今天是否已有新闻
        today_count = News.query.filter(
            db.func.date(News.timestamp) == datetime.now().date()
        ).count()

        if today_count > 100:
            print(f"✅ 今天已有 {today_count} 条新闻，跳过")
            return

        print(f"今天已有 {today_count} 条，开始采集...")

        try:
            # 澎湃新闻
            saved, dup = scrape_thepaper()

            print(f"\n{'='*70}")
            print(f"✅ 更新完成")
            print(f"新增: {saved} 条")
            print(f"重复: {dup} 条")

            total = News.query.count()
            print(f"数据库总量: {total} 条")
            print(f"{'='*70}")

        except Exception as e:
            print(f"❌ 更新失败: {e}")


def auto_start():
    """应用启动时自动执行"""

    def run_background():
        try:
            time.sleep(3)  # 等待应用完全启动
            with app.app_context():
                daily_news_update()
        except Exception as e:
            print(f"\n[新闻更新] 失败: {e}")

    t = threading.Thread(target=run_background, daemon=True)
    t.start()


if __name__ == '__main__':
    daily_news_update()
