'''
Author: your name
Date: 2026-01-19 03:08:54
LastEditTime: 2026-01-19 03:08:54
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\manage_news.py
'''
'''
Author: your name
Date: 2026-01-19 03:30:00
LastEditTime: 2026-01-19 03:30:00
LastEditors: your name
Description: 新闻和热度管理脚本
FilePath: \Q文件\python_web_project\manage_news.py
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
    
    # 每天午夜12点更新新闻
    schedule.every().day.at("00:00").do(update_daily_news)
    
    # 每天午夜12点计算热度排行
    schedule.every().day.at("00:00").do(calculate_and_save_trending_scores)
    
    # 为了测试，也可以设置每小时执行一次
    # schedule.every().hour.do(update_daily_news)
    # schedule.every().hour.do(calculate_and_save_trending_scores)
    
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


if __name__ == "__main__":
    # 可以通过命令行参数控制运行模式
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "manual":
        manual_update_news_and_trending()
    else:
        # 启动调度器
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到退出信号，正在停止调度器...")
            exit(0)