'''
Author: your name
Date: 2026-04-10 20:39:33
LastEditTime: 2026-04-10 20:39:33
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\scrape_rss_news.py
'''
"""
从真实RSS源和API爬取新闻
使用可用的新闻源获取真实新闻数据
"""

import os
import sys
from datetime import datetime, timedelta
import requests
import feedparser
import time
import random
from models import News
from app import app, db

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class RSSNewsScraper:
    """RSS新闻爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        # 可用的RSS源
        self.rss_feeds = [
            {
                'name': 'BBC中文',
                'url': 'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml',
                'source': 'BBC中文'
            },
            {
                'name': '纽约时报中文',
                'url': 'https://cn.nytimes.com/rss/',
                'source': '纽约时报'
            },
            {
                'name': '联合早报',
                'url': 'https://www.zaobao.com.sg/rss/realtime/china',
                'source': '联合早报'
            },
        ]

    def fetch_rss_news(self):
        """从RSS源获取新闻"""
        all_news = []

        for feed_info in self.rss_feeds:
            try:
                print(f"正在获取 {feed_info['name']}...")

                response = requests.get(
                    feed_info['url'],
                    headers=self.headers,
                    timeout=15
                )

                if response.status_code == 200:
                    feed = feedparser.parse(response.content)

                    for entry in feed.entries[:10]:  # 每个源取10条
                        title = entry.get('title', '')
                        link = entry.get('link', '')
                        summary = entry.get('summary', '')[:200]

                        # 解析时间
                        pub_date = datetime.now()
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            try:
                                pub_date = datetime(
                                    *entry.published_parsed[:6])
                            except:
                                pass

                        if title and len(title) > 5:
                            all_news.append({
                                'title': title,
                                'content': summary,
                                'summary': summary[:100],
                                'source': feed_info['source'],
                                'url': link,
                                'timestamp': pub_date
                            })

                    print(
                        f"  ✓ {feed_info['name']}: {len(feed.entries[:10])} 条")
                else:
                    print(
                        f"  ✗ {feed_info['name']}: 状态码 {response.status_code}")

                time.sleep(2)  # 等待2秒

            except Exception as e:
                print(f"  ✗ {feed_info['name']} 失败: {e}")

        return all_news

    def fetch_from_news_api(self):
        """从免费新闻API获取（如果有的话）"""
        # 这里可以添加NewsAPI等免费API
        # 需要API密钥，暂时跳过
        return []

    def save_news(self, news_list):
        """保存新闻到数据库"""
        saved_count = 0
        duplicate_count = 0

        for news_data in news_list:
            # 检查重复
            existing = News.query.filter_by(title=news_data['title']).first()
            if existing:
                duplicate_count += 1
                continue

            # 创建新闻
            news = News(
                title=news_data['title'],
                content=news_data.get('content', ''),
                summary=news_data.get('summary', ''),
                source=news_data.get('source', '网络新闻'),
                image_url='',
                url=news_data.get('url', ''),
                timestamp=news_data.get('timestamp', datetime.now()),
                views=random.randint(100, 5000)
            )

            db.session.add(news)
            saved_count += 1

        try:
            db.session.commit()
            return saved_count, duplicate_count
        except Exception as e:
            print(f"保存失败: {e}")
            db.session.rollback()
            return 0, duplicate_count


def scrape_real_news():
    """爬取真实新闻"""

    print("="*60)
    print("开始爬取真实新闻...")
    print("="*60)

    scraper = RSSNewsScraper()

    with app.app_context():
        # 1. 从RSS获取新闻
        print("\n1. 从RSS源获取新闻...")
        rss_news = scraper.fetch_rss_news()
        print(f"\nRSS获取: {len(rss_news)} 条")

        # 2. 保存到数据库
        if rss_news:
            print(f"\n2. 保存到数据库...")
            saved, duplicate = scraper.save_news(rss_news)
            print(f"✅ 新增: {saved} 条")
            print(f"⏭️  跳过重复: {duplicate} 条")

        # 3. 统计
        total = News.query.count()
        earliest = News.query.order_by(News.timestamp.asc()).first()
        latest = News.query.order_by(News.timestamp.desc()).first()

        print(f"\n{'='*60}")
        print(f"✅ 爬取完成！")
        print(f"数据库新闻总数: {total} 条")
        if earliest:
            print(
                f"最早: {earliest.timestamp.strftime('%Y-%m-%d %H:%M')} - {earliest.title[:50]}")
        if latest:
            print(
                f"最新: {latest.timestamp.strftime('%Y-%m-%d %H:%M')} - {latest.title[:50]}")
        print(f"{'='*60}")


if __name__ == '__main__':
    # 检查依赖
    try:
        import feedparser
    except ImportError:
        print("❌ 缺少 feedparser 库")
        print("请运行: pip install feedparser")
        sys.exit(1)

    scrape_real_news()
