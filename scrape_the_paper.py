'''
Author: your name
Date: 2026-04-11 21:59:16
LastEditTime: 2026-04-11 21:59:17
LastEditors: ZDH
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\scrape_the_paper.py
'''
"""
澎湃新闻爬虫 - 真实新闻采集
澎湃新闻新闻结构规范，易于爬取
"""

import sys
import os
import random
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from models import News
from app import app, db

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ThePaperScraper:
    """澎湃新闻爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 澎湃新闻各个频道
        self.channels = [
            {'name': '首页', 'url': 'https://www.thepaper.cn/', 'channel_id': ''},
            {'name': '时政', 'url': 'https://www.thepaper.cn/channel_25951',
                'channel_id': '25951'},
            {'name': '财经', 'url': 'https://www.thepaper.cn/channel_25952',
                'channel_id': '25952'},
            {'name': '思想', 'url': 'https://www.thepaper.cn/channel_25950',
                'channel_id': '25950'},
            {'name': '生活', 'url': 'https://www.thepaper.cn/channel_26054',
                'channel_id': '26054'},
            {'name': '问政', 'url': 'https://www.thepaper.cn/channel_25960',
                'channel_id': '25960'},
        ]

    def fetch_channel_news(self, channel):
        """从频道页面爬取新闻"""
        news_list = []
        try:
            print(f"  爬取 {channel['name']} 频道...")

            response = self.session.get(channel['url'], timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻卡片
            news_cards = soup.find_all('div', class_='news_li')
            if not news_cards:
                news_cards = soup.find_all('div', class_='video_li')

            for card in news_cards[:20]:  # 每个频道取20条
                title_tag = card.find('h2')
                if not title_tag:
                    title_tag = card.find('a')

                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)

                # 获取链接
                link_tag = card.find('a', href=True)
                if not link_tag:
                    continue

                url = link_tag.get('href', '')
                if not url.startswith('http'):
                    url = 'https://www.thepaper.cn' + url

                # 获取摘要
                summary_tag = card.find('p')
                summary = summary_tag.get_text(
                    strip=True) if summary_tag else title[:100]

                # 获取时间
                time_tag = card.find('span', class_='time')
                timestamp = datetime.now()

                if len(title) > 10 and len(title) < 100:
                    news_list.append({
                        'title': title,
                        'content': summary,
                        'summary': summary[:200],
                        'source': '澎湃新闻',
                        'url': url,
                        'timestamp': timestamp,
                        'channel': channel['name']
                    })

            print(f"    ✓ 获取 {len(news_list)} 条")

        except Exception as e:
            print(f"    ✗ 失败: {str(e)[:50]}")

        return news_list

    def fetch_news_list_api(self):
        """使用澎湃新闻的API获取新闻列表"""
        news_list = []
        try:
            print("  通过API获取新闻...")

            # 澎湃新闻的新闻列表API
            api_url = 'https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar'

            response = self.session.get(api_url, timeout=10)
            data = response.json()

            # 解析热点新闻
            hot_news = data.get('data', {}).get('hotNews', [])

            for news_item in hot_news[:20]:
                title = news_item.get('name', '')
                contId = news_item.get('contId', '')

                if title and contId:
                    url = f'https://www.thepaper.cn/newsDetail_forward_{contId}'

                    news_list.append({
                        'title': title,
                        'content': title,
                        'summary': title[:100],
                        'source': '澎湃新闻',
                        'url': url,
                        'timestamp': datetime.now()
                    })

            print(f"    ✓ API获取 {len(news_list)} 条热点新闻")

        except Exception as e:
            print(f"    ✗ API获取失败: {str(e)[:50]}")

        return news_list

    def scrape_all(self):
        """爬取所有频道"""
        all_news = []

        print("\n" + "="*70)
        print("澎湃新闻爬虫")
        print("="*70)

        # 1. 通过API获取热点新闻
        api_news = self.fetch_news_list_api()
        all_news.extend(api_news)
        time.sleep(1)

        # 2. 爬取各个频道
        for channel in self.channels:
            channel_news = self.fetch_channel_news(channel)
            all_news.extend(channel_news)
            time.sleep(random.uniform(1, 2))  # 随机等待1-2秒

        # 去重
        unique_news = []
        seen_titles = set()

        for news in all_news:
            simple_title = news['title'][:40]
            if simple_title not in seen_titles:
                seen_titles.add(simple_title)
                unique_news.append(news)

        print(f"\n去重后: {len(unique_news)} 条真实新闻")

        return unique_news


def scrape_the_paper_news():
    """爬取澎湃新闻并保存到数据库"""

    scraper = ThePaperScraper()

    with app.app_context():
        # 爬取新闻
        news_list = scraper.scrape_all()

        if not news_list:
            print("⚠️  未获取到新闻")
            return 0, 0

        # 保存到数据库
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
                source=news_data.get('source', '澎湃新闻'),
                image_url='',
                url=news_data.get('url', ''),
                timestamp=news_data.get('timestamp', datetime.now()),
                views=random.randint(100, 10000)
            )

            db.session.add(news)
            saved_count += 1

        try:
            db.session.commit()
            print(f"\n✅ 保存成功: {saved_count} 条")
            print(f"⏭️  跳过重复: {duplicate_count} 条")
            return saved_count, duplicate_count
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            db.session.rollback()
            return 0, duplicate_count


if __name__ == '__main__':
    scrape_the_paper_news()
