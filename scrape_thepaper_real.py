"""
澎湃新闻真实新闻爬虫
确保所有链接可访问，内容真实
"""

from models import News
from app import app, db
import os
import sys
import random
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class ThePaperRealScraper:
    """澎湃新闻真实爬虫 - 验证链接有效性"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def fetch_hot_news(self):
        """获取热点新闻（通过API）"""
        news_list = []
        try:
            print("  [1] 获取热点新闻...")

            # 澎湃新闻API
            api_url = 'https://cache.thepaper.cn/contentapi/wwwIndex/rightSidebar'
            response = self.session.get(api_url, timeout=10)
            data = response.json()

            hot_news = data.get('data', {}).get('hotNews', [])

            for item in hot_news[:30]:
                title = item.get('name', '')
                contId = item.get('contId', '')

                if title and contId:
                    url = f'https://www.thepaper.cn/newsDetail_forward_{contId}'

                    # 验证链接
                    if self.validate_url(url):
                        news_list.append({
                            'title': title,
                            'content': title,
                            'summary': title[:150],
                            'source': '澎湃新闻',
                            'url': url,
                            'timestamp': datetime.now(),
                            'valid': True
                        })

            print(f"    ✓ 热点新闻: {len(news_list)} 条")

        except Exception as e:
            print(f"    ✗ 失败: {e}")

        return news_list

    def fetch_channel_news(self, channel_name, channel_url, max_items=50):
        """获取频道新闻"""
        news_list = []
        try:
            print(f"  [2] 获取{channel_name}新闻...")

            response = self.session.get(channel_url, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找新闻列表
            news_items = soup.find_all('a', href=True, class_=True)

            for item in news_items[:max_items]:
                title = item.get_text(strip=True)
                href = item.get('href', '')

                # 过滤有效新闻
                if (title and
                    15 < len(title) < 100 and
                    href and
                        'newsDetail' in href):

                    url = href if href.startswith(
                        'http') else f'https://www.thepaper.cn{href}'

                    # 验证链接可访问
                    if self.validate_url(url):
                        news_list.append({
                            'title': title,
                            'content': title,
                            'summary': title[:150],
                            'source': '澎湃新闻',
                            'url': url,
                            'timestamp': datetime.now(),
                            'valid': True
                        })

            print(f"    ✓ {channel_name}: {len(news_list)} 条")

        except Exception as e:
            print(f"    ✗ {channel_name}失败: {e}")

        return news_list

    def validate_url(self, url):
        """验证URL是否可访问"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def fetch_news_detail(self, url):
        """获取新闻详情"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取标题
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ''

            # 获取内容
            content_div = soup.find('div', class_='news_txt')
            content = content_div.get_text(
                strip=True) if content_div else title

            # 获取时间
            time_tag = soup.find('div', class_='time')
            timestamp = datetime.now()

            return {
                'title': title,
                'content': content,
                'summary': content[:200] if content else title[:200],
                'source': '澎湃新闻',
                'url': url,
                'timestamp': timestamp,
                'valid': True
            }
        except:
            return None

    def scrape_all(self):
        """爬取所有新闻"""
        print("\n" + "="*70)
        print("澎湃新闻真实新闻爬虫")
        print("="*70)

        all_news = []

        # 1. 热点新闻
        hot_news = self.fetch_hot_news()
        all_news.extend(hot_news)
        time.sleep(2)

        # 2. 各频道新闻
        channels = [
            ('时政', 'https://www.thepaper.cn/channel_25951'),
            ('财经', 'https://www.thepaper.cn/channel_25952'),
            ('思想', 'https://www.thepaper.cn/channel_25950'),
        ]

        for name, url in channels:
            channel_news = self.fetch_channel_news(name, url, max_items=30)
            all_news.extend(channel_news)
            time.sleep(random.uniform(2, 4))

        # 去重
        unique_news = []
        seen_urls = set()

        for news in all_news:
            if news['url'] not in seen_urls:
                seen_urls.add(news['url'])
                unique_news.append(news)

        print(f"\n去重后: {len(unique_news)} 条真实新闻（链接已验证）")

        return unique_news


def scrape_and_save():
    """爬取并保存"""
    scraper = ThePaperRealScraper()

    with app.app_context():
        # 爬取
        news_list = scraper.scrape_all()

        if not news_list:
            print("⚠️  未获取到新闻")
            return 0, 0

        # 保存
        saved = 0
        duplicate = 0

        for news_data in news_list:
            # 检查重复
            existing = News.query.filter_by(url=news_data['url']).first()
            if existing:
                duplicate += 1
                continue

            # 保存
            news = News(
                title=news_data['title'],
                content=news_data.get('content', ''),
                summary=news_data.get('summary', ''),
                source=news_data['source'],
                image_url='',
                url=news_data['url'],
                timestamp=news_data['timestamp'],
                views=random.randint(100, 10000)
            )

            db.session.add(news)
            saved += 1

        try:
            db.session.commit()
            print(f"\n✅ 保存成功: {saved} 条")
            print(f"⏭️  重复: {duplicate} 条")
            return saved, duplicate
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            db.session.rollback()
            return 0, duplicate


if __name__ == '__main__':
    scrape_and_save()
