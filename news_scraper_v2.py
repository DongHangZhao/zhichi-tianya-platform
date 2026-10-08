'''
Author: your name
Date: 2026-03-15 02:41:56
LastEditTime: 2026-03-15 02:41:56
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\news_scraper_v2.py
'''
"""
新闻采集器模块 V2 - 优化版
从多个来源自动抓取真实新闻数据，包括图文和视频
"""

import os
import re
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


class NewsScraper:
    """新闻采集器"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }

    def fetch_xinhua_news(self):
        """抓取新华网新闻"""
        news_list = []
        try:
            print("  正在连接新华网...")
            response = requests.get('http://www.xinhuanet.com/politics/',
                                    headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有链接
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                title = link.get_text(strip=True)
                url = link.get('href', '')

                # 过滤有效新闻
                if (title and len(title) > 8 and len(title) < 80 and
                        url and ('xinhuanet.com' in url or url.startswith('/'))):

                    if not url.startswith('http'):
                        url = 'http://www.xinhuanet.com' + url.lstrip('/')

                    # 排除非新闻链接
                    if not any(x in url for x in ['video', 'forum', 'blog', 'photo']):
                        news_list.append({
                            'title': title,
                            'source': '新华网',
                            'url': url,
                            'type': 'general'
                        })

            print(f"  ✓ 新华网抓取成功：{len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 新华网抓取失败：{e}")

        return news_list[:10]  # 限制最多 10 条

    def fetch_people_daily_news(self):
        """抓取人民网新闻"""
        news_list = []
        try:
            print("  正在连接人民网...")
            response = requests.get('http://politics.people.com.cn/',
                                    headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有链接
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                title = link.get_text(strip=True)
                url = link.get('href', '')

                # 跳过无效链接
                if not url or url.startswith('#') or url.startswith('javascript'):
                    continue

                # 构建完整 URL
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = 'http://politics.people.com.cn' + url
                    else:
                        continue

                # 过滤标题
                if (title and len(title) > 8 and len(title) < 80 and
                        'people.com.cn' in url):
                    news_list.append({
                        'title': title,
                        'source': '人民网',
                        'url': url,
                        'type': 'general'
                    })

            print(f"  ✓ 人民网抓取成功：{len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 人民网抓取失败：{e}")

        return news_list[:10]

    def fetch_cctv_video(self):
        """抓取央视新闻视频"""
        news_list = []
        try:
            print("  正在连接央视新闻...")
            response = requests.get('https://www.cctv.com/',
                                    headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找视频链接
            video_links = soup.find_all('a', href=True)

            for link in video_links:
                title = link.get_text(strip=True)
                url = link.get('href', '')

                if (title and len(title) > 8 and len(title) < 80 and
                        url and 'cctv.com' in url):
                    news_list.append({
                        'title': title,
                        'source': '央视新闻',
                        'url': url,
                        'type': 'video'
                    })

            print(f"  ✓ 央视新闻抓取成功：{len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 央视新闻抓取失败：{e}")

        return news_list[:8]

    def fetch_thepaper_news(self):
        """抓取澎湃新闻"""
        news_list = []
        try:
            print("  正在连接澎湃新闻...")
            response = requests.get('https://www.thepaper.cn/',
                                    headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有链接
            all_links = soup.find_all('a', href=True)

            for link in all_links:
                title = link.get_text(strip=True)
                url = link.get('href', '')

                if not url or url.startswith('#'):
                    continue

                # 构建完整 URL
                if not url.startswith('http'):
                    if url.startswith('/'):
                        url = 'https://www.thepaper.cn' + url
                    else:
                        continue

                # 过滤标题
                if (title and len(title) > 8 and len(title) < 80 and
                        'thepaper.cn' in url):
                    news_list.append({
                        'title': title,
                        'source': '澎湃新闻',
                        'url': url,
                        'type': 'general'
                    })

            print(f"  ✓ 澎湃新闻抓取成功：{len(news_list)} 条")

        except Exception as e:
            print(f"  ✗ 澎湃新闻抓取失败：{e}")

        return news_list[:10]

    def scrape_all(self):
        """抓取所有来源的新闻"""
        print("\n" + "="*50)
        print("开始抓取新闻...")
        print("="*50)

        all_news = []

        # 新华网（最稳定）
        xinhua_news = self.fetch_xinhua_news()
        all_news.extend(xinhua_news)

        # 人民网
        people_news = self.fetch_people_daily_news()
        all_news.extend(people_news)

        # 央视新闻
        cctv_news = self.fetch_cctv_video()
        all_news.extend(cctv_news)

        # 澎湃新闻
        thepaper_news = self.fetch_thepaper_news()
        all_news.extend(thepaper_news)

        print("="*50)
        print(f"共抓取 {len(all_news)} 条新闻")
        print("="*50)

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
                'content': content[:2000],
                'image_url': image_url
            }
        except Exception as e:
            print(f"  获取详情失败：{e}")
            return {'content': '', 'image_url': None}


def save_scraper_news(news_list):
    """保存抓取的新闻到数据库"""
    from app import app, db
    from models import News

    with app.app_context():
        saved_count = 0
        duplicate_count = 0
        failed_count = 0

        for news_item in news_list:
            try:
                # 检查是否已存在（按标题去重）
                existing = News.query.filter_by(
                    title=news_item['title']).first()
                if existing:
                    duplicate_count += 1
                    continue

                # 获取详情（可选，如果需要详细内容）
                # scraper = NewsScraper()
                # detail = scraper.get_news_detail(news_item['url'])

                # 创建新闻记录
                news = News(
                    title=news_item['title'],
                    content=f"查看详情：{news_item['url']}",
                    summary=news_item['title'][:100] + "...",
                    source=news_item['source'],
                    image_url=None,  # 暂时不保存图片
                    timestamp=datetime.now()
                )

                db.session.add(news)
                saved_count += 1

            except Exception as e:
                print(f"  保存失败 {news_item['title']}: {e}")
                failed_count += 1

        db.session.commit()

        print(f"\n保存结果:")
        print(f"  ✓ 成功保存：{saved_count} 条")
        print(f"  ⚠ 重复跳过：{duplicate_count} 条")
        print(f"  ✗ 保存失败：{failed_count} 条")

        return saved_count


if __name__ == '__main__':
    scraper = NewsScraper()
    news_list = scraper.scrape_all()

    if news_list:
        print(f"\n准备保存 {len(news_list)} 条新闻到数据库...")
        save_scraper_news(news_list)
        print("\n✅ 抓取完成！")
    else:
        print("\n❌ 未能抓取到任何新闻")
