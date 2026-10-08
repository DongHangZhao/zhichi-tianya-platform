'''
Author: your name
Date: 2026-04-10 20:37:22
LastEditTime: 2026-04-10 20:37:22
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\scrape_real_historical_news.py
'''
"""
爬取真实历史新闻数据
时间范围：2026年1月1日 - 2026年4月10日
从真实新闻网站抓取，包含原文链接
"""

import os
import sys
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import time
import random
from models import News
from app import app, db

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class RealNewsScraper:
    """真实新闻爬虫"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_from_baidu_news(self, date_str):
        """从百度新闻搜索抓取指定日期的新闻"""
        news_list = []
        try:
            # 百度新闻搜索URL，按时间筛选
            url = f'https://www.baidu.com/s?wd=新闻&pn=0&rn=10&gpc=stf={date_str},{date_str}|stftype=1'

            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析搜索结果
            results = soup.find_all('div', class_='result c-container')

            for result in results[:5]:  # 只取前5条
                title_tag = result.find('h3', class_='t')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue

                link = link_tag.get('href', '')

                # 获取摘要
                summary_tag = result.find('span', class_='content-right_8TVD1')
                summary = summary_tag.get_text(
                    strip=True) if summary_tag else title[:100]

                # 获取来源
                source_tag = result.find('span', class_='source')
                source = source_tag.get_text(
                    strip=True) if source_tag else '百度新闻'

                if title and len(title) > 5:
                    news_list.append({
                        'title': title,
                        'content': summary,
                        'summary': summary[:100],
                        'source': source,
                        'url': link,
                        'timestamp': datetime.strptime(date_str, '%Y-%m-%d')
                    })

            print(f"  ✓ 百度新闻({date_str}): {len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 百度新闻失败: {e}")

        return news_list

    def fetch_from_sogou_news(self, date_str):
        """从搜狗搜索抓取新闻"""
        news_list = []
        try:
            url = f'https://www.sogou.com/web?query=新闻&searchtime={date_str}'

            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            results = soup.find_all('div', class_='vrwrap')

            for result in results[:5]:
                title_tag = result.find('h3')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue

                link = link_tag.get('href', '')

                # 摘要
                summary_tag = result.find('p', class_='ft')
                summary = summary_tag.get_text(
                    strip=True) if summary_tag else title[:100]

                # 来源
                source_tag = result.find('a', class_='u')
                source = source_tag.get_text(
                    strip=True) if source_tag else '搜狗新闻'

                if title and len(title) > 5:
                    news_list.append({
                        'title': title,
                        'content': summary,
                        'summary': summary[:100],
                        'source': source,
                        'url': link,
                        'timestamp': datetime.strptime(date_str, '%Y-%m-%d')
                    })

            print(f"  ✓ 搜狗新闻({date_str}): {len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 搜狗新闻失败: {e}")

        return news_list

    def fetch_xinhua_archive(self, date_str):
        """从新华网档案获取新闻"""
        news_list = []
        try:
            # 新华网新闻档案
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            url = f'http://www.xinhuanet.com/{date_obj.year}-{date_obj.month:02d}/{date_obj.day:02d}/'

            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻链接
            links = soup.find_all('a')

            for link in links[:10]:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                if title and len(title) > 8 and len(title) < 80 and href:
                    if 'xinhuanet.com' in href or href.startswith('/'):
                        if not href.startswith('http'):
                            href = 'http://www.xinhuanet.com' + href

                        news_list.append({
                            'title': title,
                            'content': title,
                            'summary': title[:100],
                            'source': '新华网',
                            'url': href,
                            'timestamp': date_obj
                        })

            print(f"  ✓ 新华网档案({date_str}): {len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 新华网档案失败: {e}")

        return news_list

    def save_news_to_db(self, news_list):
        """保存新闻到数据库"""
        saved_count = 0
        duplicate_count = 0

        for news_data in news_list:
            # 检查是否已存在
            existing = News.query.filter_by(
                title=news_data['title']
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # 创建新闻
            news = News(
                title=news_data['title'],
                content=news_data.get('content', ''),
                summary=news_data.get('summary', ''),
                source=news_data.get('source', '网络新闻'),
                image_url=news_data.get('image_url', ''),
                url=news_data.get('url', ''),  # 保存原文链接
                timestamp=news_data.get('timestamp', datetime.now()),
                views=random.randint(100, 5000)
            )

            db.session.add(news)
            saved_count += 1

        try:
            db.session.commit()
            return saved_count, duplicate_count
        except Exception as e:
            print(f"  ✗ 保存失败: {e}")
            db.session.rollback()
            return 0, duplicate_count


def scrape_historical_news():
    """爬取历史新闻"""

    # 时间范围
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 4, 10)

    # 计算总天数
    total_days = (end_date - start_date).days + 1

    print(f"开始爬取真实历史新闻...")
    print(
        f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"总计: {total_days} 天")
    print(f"{'='*60}")

    scraper = RealNewsScraper()
    total_saved = 0
    total_duplicate = 0

    with app.app_context():
        # 每隔几天爬取一次（避免过于频繁）
        day_step = 2  # 每2天爬取一次

        for day_offset in range(0, total_days, day_step):
            current_date = start_date + timedelta(days=day_offset)
            date_str = current_date.strftime('%Y-%m-%d')

            print(f"\n爬取日期: {date_str}")

            # 从多个源爬取
            all_news = []

            # 1. 百度新闻
            baidu_news = scraper.fetch_from_baidu_news(date_str)
            all_news.extend(baidu_news)

            time.sleep(2)  # 等待2秒

            # 2. 搜狗新闻
            # sogou_news = scraper.fetch_from_sogou_news(date_str)
            # all_news.extend(sogou_news)

            # time.sleep(2)

            # 3. 新华网档案
            xinhua_news = scraper.fetch_xinhua_archive(date_str)
            all_news.extend(xinhua_news)

            # 去重（基于标题）
            unique_news = []
            seen_titles = set()
            for news in all_news:
                if news['title'] not in seen_titles:
                    seen_titles.add(news['title'])
                    unique_news.append(news)

            print(f"  去重后: {len(unique_news)} 条")

            # 保存到数据库
            if unique_news:
                saved, duplicate = scraper.save_news_to_db(unique_news)
                total_saved += saved
                total_duplicate += duplicate
                print(f"  ✅ 保存: {saved} 条, 重复: {duplicate} 条")

            # 等待3-5秒，避免被封
            wait_time = random.uniform(3, 5)
            time.sleep(wait_time)

        print(f"\n{'='*60}")
        print(f"✅ 爬取完成！")
        print(f"新增新闻: {total_saved} 条")
        print(f"跳过重复: {total_duplicate} 条")
        print(
            f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")


if __name__ == '__main__':
    scrape_historical_news()
