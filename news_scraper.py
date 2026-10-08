'''
Author: your name
Date: 2026-03-15 02:03:33
LastEditTime: 2026-03-15 02:03:33
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\news_scraper.py
'''
"""
新闻采集器模块
从多个来源自动抓取新闻数据，包括图文和视频
"""

from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
import re
import os
import sys
from utils import save_image
from models import db, News

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class NewsScraper:
    """新闻采集器"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        # 国内新闻源列表（真实可用的 RSS 和 API）
        self.news_sources = [
            {
                'name': '新华网',
                'url': 'http://www.xinhuanet.com/politics/',
                'type': 'general'
            },
            {
                'name': '人民网',
                'url': 'http://politics.people.com.cn/',
                'type': 'general'
            },
            {
                'name': '央视新闻',
                'url': 'https://www.cctv.com/',
                'type': 'video'
            },
            {
                'name': '澎湃新闻',
                'url': 'https://www.thepaper.cn/',
                'type': 'general'
            },
            {
                'name': '今日头条热点',
                'url': 'https://www.toutiao.com/',
                'type': 'general'
            }
        ]

    def fetch_xinhua_news(self):
        """抓取新华网新闻"""
        news_list = []
        try:
            response = requests.get('http://www.xinhuanet.com/politics/',
                                    headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻链接
            news_items = soup.find_all(
                'a', href=re.compile(r'/\d{4}-\d{2}/\d{2}/c_'))

            for item in news_items[:10]:  # 限制每条来源最多 10 条
                title = item.get_text(strip=True)
                url = item['href']

                if not url.startswith('http'):
                    url = 'http://www.xinhuanet.com' + url

                if title and len(title) > 5:  # 过滤无效标题
                    news_list.append({
                        'title': title,
                        'source': '新华网',
                        'url': url,
                        'type': 'general'
                    })
        except Exception as e:
            print(f"抓取新华网失败：{e}")

        return news_list

    def fetch_people_daily_news(self):
        """抓取人民网新闻"""
        news_list = []
        try:
            response = requests.get('http://politics.people.com.cn/',
                                    headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻
            news_items = soup.find_all('a', href=True)

            for item in news_items[:10]:
                title = item.get_text(strip=True)
                url = item['href']

                if not url.startswith('http'):
                    url = 'http://politics.people.com.cn' + url

                if title and len(title) > 5 and 'content' in url:
                    news_list.append({
                        'title': title,
                        'source': '人民网',
                        'url': url,
                        'type': 'general'
                    })
        except Exception as e:
            print(f"抓取人民网失败：{e}")

        return news_list

    def fetch_cctv_video(self):
        """抓取央视新闻视频"""
        news_list = []
        try:
            response = requests.get('https://www.cctv.com/',
                                    headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找视频新闻
            video_items = soup.find_all(
                'a', {'class': re.compile(r'.*video.*|.*news.*')})

            for item in video_items[:8]:
                title = item.get_text(strip=True)
                url = item.get('href', '')

                if title and len(title) > 5 and url:
                    news_list.append({
                        'title': title,
                        'source': '央视新闻',
                        'url': url,
                        'type': 'video'
                    })
        except Exception as e:
            print(f"抓取央视新闻失败：{e}")

        return news_list

    def fetch_thepaper_news(self):
        """抓取澎湃新闻"""
        news_list = []
        try:
            response = requests.get('https://www.thepaper.cn/',
                                    headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻
            news_items = soup.find_all(
                'div', {'class': re.compile(r'.*newsitem.*|.*list.*')})

            for item in news_items[:10]:
                title_elem = item.find('a') or item.find(
                    'h2') or item.find('h3')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url = title_elem.get('href', '')

                    if not url.startswith('http'):
                        url = 'https://www.thepaper.cn' + url

                    if title and len(title) > 5:
                        news_list.append({
                            'title': title,
                            'source': '澎湃新闻',
                            'url': url,
                            'type': 'general'
                        })
        except Exception as e:
            print(f"抓取澎湃新闻失败：{e}")

        return news_list

    def scrape_all(self):
        """抓取所有来源的新闻"""
        all_news = []

        print("开始抓取新华网...")
        all_news.extend(self.fetch_xinhua_news())

        print("开始抓取人民网...")
        all_news.extend(self.fetch_people_daily_news())

        print("开始抓取央视新闻...")
        all_news.extend(self.fetch_cctv_video())

        print("开始抓取澎湃新闻...")
        all_news.extend(self.fetch_thepaper_news())

        print(f"共抓取 {len(all_news)} 条新闻")
        return all_news

    def get_news_detail(self, url):
        """获取新闻详情内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取内容
            content_div = soup.find(
                'div', {'class': re.compile(r'.*content.*|.*article.*')})
            if not content_div:
                content_div = soup.find('article')

            content = ""
            image_url = None

            if content_div:
                # 提取文本
                paragraphs = content_div.find_all('p')
                content = '\n'.join([p.get_text(strip=True)
                                    for p in paragraphs if p.get_text(strip=True)])

                # 提取第一张图片
                img = content_div.find('img')
                if img:
                    image_url = img.get('src') or img.get('data-src')

            return {
                'content': content[:2000],  # 限制长度
                'image_url': image_url
            }
        except Exception as e:
            print(f"获取新闻详情失败：{e}")
            return {'content': '', 'image_url': None}


def save_scraper_news(news_list):
    """保存抓取的新闻到数据库"""
    from app import app, db

    with app.app_context():
        saved_count = 0
        duplicate_count = 0

        for news_item in news_list:
            # 检查是否已存在
            existing = News.query.filter_by(title=news_item['title']).first()
            if existing:
                duplicate_count += 1
                continue

            # 获取详情
            scraper = NewsScraper()
            detail = scraper.get_news_detail(news_item['url'])

            # 创建新闻记录
            news = News(
                title=news_item['title'],
                content=detail['content'] or f"查看详情：{news_item['url']}",
                summary=news_item['title'][:100] + "...",
                source=news_item['source'],
                image_url=detail['image_url'],
                timestamp=datetime.now()
            )

            db.session.add(news)
            saved_count += 1

        db.session.commit()
        print(f"保存新闻：{saved_count} 条，重复：{duplicate_count} 条")
        return saved_count


if __name__ == '__main__':
    scraper = NewsScraper()
    news_list = scraper.scrape_all()
    save_scraper_news(news_list)
