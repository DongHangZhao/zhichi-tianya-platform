'''
Author: your name
Date: 2026-03-15 02:04:59
LastEditTime: 2026-03-15 02:04:59
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\scheduler.py
'''
"""
定时任务模块
每天自动执行新闻抓取任务
"""

from news_scraper_v2 import NewsScraper, save_scraper_news
from datetime import datetime
import threading
import schedule
import time


# 延迟导入 app，避免循环依赖
def get_app():
    """获取 app 实例"""
    from app import app
    return app


class ScheduledTasks:
    """定时任务管理器"""

    def __init__(self):
        self.running = False

    def daily_news_fetch(self):
        """每日新闻抓取任务"""
        print(f"\n[{datetime.now()}] 开始执行每日新闻抓取任务...")

        try:
            app = get_app()
            with app.app_context():
                scraper = NewsScraper()
                news_list = scraper.scrape_all()
                saved_count = save_scraper_news(news_list)

                print(f"[{datetime.now()}] 每日新闻抓取完成，保存 {saved_count} 条新闻")
        except Exception as e:
            print(f"[{datetime.now()}] 每日新闻抓取失败：{e}")

    def run_scheduler(self):
        """运行定时任务调度器"""
        # 每天早上 8 点执行
        schedule.every().day.at("08:00").do(self.daily_news_fetch)

        # 每 6 小时执行一次（可选，用于测试）
        # schedule.every(6).hours.do(self.daily_news_fetch)

        print("定时任务已启动，将在每天 08:00 自动抓取新闻")

        self.running = True
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次

    def start(self):
        """启动定时任务线程"""
        scheduler_thread = threading.Thread(
            target=self.run_scheduler, daemon=True)
        scheduler_thread.start()
        print("定时任务线程已启动")

    def stop(self):
        """停止定时任务"""
        self.running = False
        schedule.clear()
        print("定时任务已停止")


# 全局定时器实例
scheduler = ScheduledTasks()


def init_scheduler():
    """初始化并启动定时任务"""
    scheduler.start()


if __name__ == '__main__':
    # 手动测试
    print("手动执行一次新闻抓取...")
    scheduler.daily_news_fetch()

    print("\n启动定时任务...")
    scheduler.start()

    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop()
