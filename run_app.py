'''
Author: your name
Date: 2026-01-19 03:51:10
LastEditTime: 2026-01-19 03:51:10
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\run_app.py
'''
from app import app
import threading
import time
from scrape_news import update_daily_news
from calculate_trending import calculate_daily_trending
import schedule

def run_scheduled_tasks():
    """运行定时任务"""
    # 设置每日更新任务
    schedule.every().day.at("00:00").do(update_daily_news)  # 每天午夜更新新闻
    schedule.every().day.at("00:05").do(calculate_daily_trending)  # 每天00:05计算热度排行
    
    # 为了测试，我们也每小时执行一次
    schedule.every().hour.do(update_daily_news)
    schedule.every().hour.do(calculate_daily_trending)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == '__main__':
    # 启动定时任务线程
    scheduler_thread = threading.Thread(target=run_scheduled_tasks, daemon=True)
    scheduler_thread.start()
    
    print("定时任务已启动...")
    print("新闻更新任务: 每小时执行")
    print("热度计算任务: 每小时执行")
    print("启动Web服务器...")
    
    # 启动Web服务器
    app.run(debug=True, host='0.0.0.0', port=5000)