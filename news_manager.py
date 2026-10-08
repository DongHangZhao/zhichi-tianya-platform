'''
Author: your name
Date: 2026-01-19 03:08:54
LastEditTime: 2026-01-19 03:08:54
LastEditors: your name
Description: 新闻和热度管理脚本
FilePath: \Q文件\python_web_project\news_manager.py
'''

"""
新闻和热度管理脚本
用于自动化每日新闻更新和热度排行计算
"""

import schedule
import time
from datetime import datetime
import threading
from app import app, db
from scrape_news import update_daily_news
from calculate_trending import calculate_and_save_trending_scores

def run_scheduler():
    """
    运行调度器
    """
    print(f"[{datetime.now()}] 启动新闻和热度管理调度器...")
    
    # 每天早上6点更新新闻
    schedule.every().day.at("06:00").do(update_daily_news)
    
    # 每天中午12点计算热度排行
    schedule.every().day.at("12:00").do(calculate_and_save_trending_scores)
    
    # 每天晚上10点再次更新新闻
    schedule.every().day.at("22:00").do(update_daily_news)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


def manual_update_news_and_trending():
    """
    手动执行新闻更新和热度计算
    """
    print(f"[{datetime.now()}] 开始手动更新新闻和热度排行...")
    
    with app.app_context():
        # 更新新闻
        update_daily_news()
        print(f"[{datetime.now()}] 新闻更新完成")
        
        # 计算热度排行
        calculate_and_save_trending_scores()
        print(f"[{datetime.now()}] 热度排行计算完成")
    
    print(f"[{datetime.now()}] 手动更新和计算完成")


def get_news_statistics():
    """
    获取新闻统计信息
    """
    with app.app_context():
        from models import News
        total_news = News.query.count()
        latest_news = News.query.order_by(News.timestamp.desc()).first()
        
        stats = {
            'total_news': total_news,
            'latest_news_title': latest_news.title if latest_news else 'N/A',
            'latest_news_time': latest_news.timestamp if latest_news else None,
            'update_time': datetime.now()
        }
        
        return stats


if __name__ == "__main__":
    # 可以通过命令行参数控制运行模式
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "manual":
            manual_update_news_and_trending()
        elif sys.argv[1] == "stats":
            stats = get_news_statistics()
            print(f"新闻总数: {stats['total_news']}")
            print(f"最新新闻: {stats['latest_news_title']}")
            print(f"更新时间: {stats['update_time']}")
        elif sys.argv[1] == "now":
            # 立即执行一次更新
            with app.app_context():
                update_daily_news()
    else:
        # 启动调度器
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # 保持主线程运行
        try:
            print("新闻管理调度器已启动，按 Ctrl+C 停止...")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止调度器...")
            exit(0)