'''
Author: your name
Date: 2026-03-15 02:15:01
LastEditTime: 2026-03-15 02:15:01
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\test_news_scraper.py
'''
"""
快速测试脚本
测试新闻抓取功能是否正常工作
"""

from news_scraper import NewsScraper, save_scraper_news
from models import db, News
from app import app


def test_scraper():
    """测试新闻抓取"""
    print("=" * 50)
    print("开始测试新闻抓取功能")
    print("=" * 50)

    # 创建抓取器实例
    scraper = NewsScraper()

    # 测试单个来源
    print("\n1. 测试新华网抓取...")
    xinhua_news = scraper.fetch_xinhua_news()
    print(f"   抓取到 {len(xinhua_news)} 条新华网新闻")
    if xinhua_news:
        print(f"   示例：{xinhua_news[0]['title'][:50]}...")

    print("\n2. 测试人民网抓取...")
    people_news = scraper.fetch_people_daily_news()
    print(f"   抓取到 {len(people_news)} 条人民网新闻")
    if people_news:
        print(f"   示例：{people_news[0]['title'][:50]}...")

    print("\n3. 测试央视新闻抓取...")
    cctv_news = scraper.fetch_cctv_video()
    print(f"   抓取到 {len(cctv_news)} 条央视新闻")
    if cctv_news:
        print(f"   示例：{cctv_news[0]['title'][:50]}...")

    print("\n4. 测试澎湃新闻抓取...")
    thepaper_news = scraper.fetch_thepaper_news()
    print(f"   抓取到 {len(thepaper_news)} 条澎湃新闻")
    if thepaper_news:
        print(f"   示例：{thepaper_news[0]['title'][:50]}...")

    # 测试全部抓取
    print("\n5. 测试全部来源抓取...")
    all_news = scraper.scrape_all()
    print(f"   共抓取 {len(all_news)} 条新闻")

    # 测试保存到数据库
    print("\n6. 测试保存到数据库...")
    with app.app_context():
        saved_count = save_scraper_news(all_news)
        print(f"   成功保存 {saved_count} 条新闻")

        # 查询数据库
        total_news = News.query.count()
        print(f"   数据库中共有 {total_news} 条新闻")

        # 显示最新新闻
        latest = News.query.order_by(News.timestamp.desc()).first()
        if latest:
            print(f"\n   最新新闻：{latest.title}")
            print(f"   来源：{latest.source}")
            print(f"   时间：{latest.timestamp}")

    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)


if __name__ == '__main__':
    test_scraper()
