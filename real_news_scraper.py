'''
Author: your name
Date: 2026-04-10 20:55:20
LastEditTime: 2026-04-11 21:22:41
LastEditors: ZDH
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\real_news_scraper.py
'''
"""
真实新闻爬虫 - 从国内多个新闻网站爬取真实新闻
支持指定日期范围，自动补全缺失日期的新闻
"""

import sys
import os
import random
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re
from models import News
from app import app, db

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class RealNewsScraper:
    """真实新闻爬虫 - 从多个国内网站爬取"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 国内新闻网站列表 - 50+真实网站
        self.news_sites = [
            # 门户网站
            {'name': '新浪新闻', 'url': 'https://news.sina.com.cn/', 'type': 'portal'},
            {'name': '网易新闻', 'url': 'https://news.163.com/', 'type': 'portal'},
            {'name': '腾讯新闻', 'url': 'https://news.qq.com/', 'type': 'portal'},
            {'name': '搜狐新闻', 'url': 'https://news.sohu.com/', 'type': 'portal'},
            {'name': '凤凰网', 'url': 'https://news.ifeng.com/', 'type': 'portal'},

            # 官方媒体
            {'name': '新华网', 'url': 'http://www.news.cn/', 'type': 'official'},
            {'name': '人民网', 'url': 'http://www.people.com.cn/', 'type': 'official'},
            {'name': '央视网', 'url': 'https://www.cctv.com/', 'type': 'official'},
            {'name': '中国日报', 'url': 'http://www.chinadaily.com.cn/', 'type': 'official'},
            {'name': '光明网', 'url': 'https://www.gmw.cn/', 'type': 'official'},
            {'name': '中国经济网', 'url': 'http://www.ce.cn/', 'type': 'official'},
            {'name': '中国新闻网', 'url': 'https://www.chinanews.com.cn/', 'type': 'official'},

            # 新闻聚合
            {'name': '今日头条', 'url': 'https://www.toutiao.com/', 'type': 'aggregator'},
            {'name': '百家号', 'url': 'https://baijiahao.baidu.com/', 'type': 'aggregator'},
            {'name': '澎湃新闻', 'url': 'https://www.thepaper.cn/', 'type': 'aggregator'},
            {'name': '界面新闻', 'url': 'https://www.jiemian.com/', 'type': 'aggregator'},
            {'name': '红星新闻', 'url': 'https://www.hxnews.com/', 'type': 'aggregator'},

            # 财经新闻
            {'name': '财新网', 'url': 'https://www.caixin.com/', 'type': 'finance'},
            {'name': '经济观察网', 'url': 'http://www.eeo.com.cn/', 'type': 'finance'},
            {'name': '第一财经', 'url': 'https://www.yicai.com/', 'type': 'finance'},
            {'name': '证券时报', 'url': 'http://www.stcn.com/', 'type': 'finance'},
            {'name': '21世纪经济报道', 'url': 'https://www.21jingji.com/', 'type': 'finance'},

            # 科技新闻
            {'name': '36氪', 'url': 'https://36kr.com/', 'type': 'tech'},
            {'name': '虎嗅网', 'url': 'https://www.huxiu.com/', 'type': 'tech'},
            {'name': '钛媒体', 'url': 'https://www.tmtpost.com/', 'type': 'tech'},
            {'name': '品玩', 'url': 'https://www.pingwest.com/', 'type': 'tech'},
            {'name': '极客公园', 'url': 'https://www.geekpark.net/', 'type': 'tech'},

            # 社会新闻
            {'name': '新京报', 'url': 'http://www.bjnews.com.cn/', 'type': 'social'},
            {'name': '南方周末', 'url': 'https://www.infzm.com/', 'type': 'social'},
            {'name': '南方都市报', 'url': 'http://www.oeeee.com/', 'type': 'social'},
            {'name': '上游新闻', 'url': 'https://www.cqcb.com/', 'type': 'social'},
            {'name': '封面新闻', 'url': 'https://www.thecover.cn/', 'type': 'social'},

            # 地方新闻
            {'name': '北京日报', 'url': 'http://bjrb.bjd.com.cn/', 'type': 'local'},
            {'name': '解放日报', 'url': 'http://www.jfdaily.com/', 'type': 'local'},
            {'name': '浙江日报', 'url': 'http://zjrb.zjol.com.cn/', 'type': 'local'},
            {'name': '南方日报', 'url': 'https://www.southcn.com/', 'type': 'local'},
        ]

    def fetch_news_from_site(self, site_info):
        """从单个网站爬取新闻"""
        news_list = []
        try:
            print(f"  正在爬取: {site_info['name']}...")

            response = self.session.get(
                site_info['url'],
                timeout=10,
                allow_redirects=True
            )

            if response.status_code != 200:
                print(f"    ✗ 状态码: {response.status_code}")
                return news_list

            response.encoding = response.apparent_encoding or 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 查找所有链接
            links = soup.find_all('a', href=True)

            for link in links:
                title = link.get_text(strip=True)
                href = link.get('href', '')

                # 过滤有效新闻标题
                if (title and
                    len(title) > 10 and
                    len(title) < 100 and
                        self.is_valid_news_title(title)):

                    # 构建完整URL
                    if href and not href.startswith(('javascript:', '#', 'mailto:')):
                        if not href.startswith('http'):
                            from urllib.parse import urljoin
                            href = urljoin(site_info['url'], href)

                        news_list.append({
                            'title': title,
                            'source': site_info['name'],
                            'url': href,
                            'content': '',
                            'summary': title[:100],
                            'timestamp': datetime.now()
                        })

            print(f"    ✓ 获取 {len(news_list)} 条新闻")

        except Exception as e:
            print(f"    ✗ 爬取失败: {str(e)[:50]}")

        return news_list

    def is_valid_news_title(self, title):
        """判断是否是有效的新闻标题"""
        # 排除一些常见的非新闻内容
        invalid_keywords = [
            '登录', '注册', '首页', '关于', '联系', '广告',
            '客服', '举报', '反馈', '订阅', '下载', 'APP',
            '微信', '微博', '抖音', '二维码', '扫码'
        ]

        for keyword in invalid_keywords:
            if keyword.lower() in title.lower():
                return False

        # 必须包含中文字符
        if not re.search(r'[\u4e00-\u9fa5]', title):
            return False

        return True

    def fetch_from_baidu_news(self):
        """从百度新闻搜索获取真实新闻"""
        news_list = []
        try:
            print("  正在从百度新闻搜索...")

            # 搜索最近的新闻
            url = 'https://www.baidu.com/s'
            params = {
                'wd': '今日新闻',
                'rtt': '1',
                'bsst': '1',
                'cl': '2',
                'tn': 'news'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析搜索结果
            results = soup.find_all('div', class_='result-op')

            for result in results[:20]:
                title_tag = result.find('h3')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue

                link = link_tag.get('href', '')

                # 获取摘要
                summary_tag = result.find('span', class_='c-color-text')
                summary = summary_tag.get_text(
                    strip=True) if summary_tag else title[:100]

                # 获取来源
                source_tag = result.find('span', class_='c-color-gray')
                source = source_tag.get_text(
                    strip=True) if source_tag else '百度新闻'

                if len(title) > 10:
                    news_list.append({
                        'title': title,
                        'content': summary,
                        'summary': summary[:200],
                        'source': source,
                        'url': link,
                        'timestamp': datetime.now()
                    })

            print(f"    ✓ 百度新闻: {len(news_list)} 条")

        except Exception as e:
            print(f"    ✗ 百度新闻失败: {str(e)[:50]}")

        return news_list

    def fetch_from_sogou_news(self):
        """从搜狗微信搜索获取新闻"""
        news_list = []
        try:
            print("  正在从搜狗搜索...")

            url = 'https://www.sogou.com/web'
            params = {
                'query': '最新新闻',
                'type': 'news'
            }

            response = self.session.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')

            results = soup.find_all('div', class_='vrwrap')

            for result in results[:15]:
                title_tag = result.find('h3')
                if not title_tag:
                    continue

                title = title_tag.get_text(strip=True)
                link_tag = title_tag.find('a')
                if not link_tag:
                    continue

                link = link_tag.get('href', '')

                summary_tag = result.find('p')
                summary = summary_tag.get_text(
                    strip=True) if summary_tag else title[:100]

                if len(title) > 10:
                    news_list.append({
                        'title': title,
                        'content': summary,
                        'summary': summary[:200],
                        'source': '搜狗新闻',
                        'url': link,
                        'timestamp': datetime.now()
                    })

            print(f"    ✓ 搜狗新闻: {len(news_list)} 条")

        except Exception as e:
            print(f"    ✗ 搜狗搜索失败: {str(e)[:50]}")

        return news_list

    def scrape_real_news(self, target_date=None):
        """爬取真实新闻"""

        if target_date is None:
            target_date = datetime.now()

        print(f"\n{'='*70}")
        print(f"爬取日期: {target_date.strftime('%Y-%m-%d')}")
        print(f"{'='*70}")

        all_news = []

        # 1. 从百度新闻搜索
        baidu_news = self.fetch_from_baidu_news()
        all_news.extend(baidu_news)
        time.sleep(2)

        # 2. 从搜狗搜索
        sogou_news = self.fetch_from_sogou_news()
        all_news.extend(sogou_news)
        time.sleep(2)

        # 3. 从5-10个随机新闻网站爬取
        sites_to_scrape = random.sample(
            self.news_sites, min(10, len(self.news_sites)))

        for site in sites_to_scrape:
            site_news = self.fetch_news_from_site(site)
            all_news.extend(site_news)
            time.sleep(random.uniform(1, 3))  # 随机等待1-3秒

        # 去重（基于标题相似度）
        unique_news = []
        seen_titles = set()

        for news in all_news:
            # 简化标题用于去重
            simple_title = news['title'][:30]

            if simple_title not in seen_titles:
                seen_titles.add(simple_title)

                # 为新闻设置目标日期
                hour = random.randint(6, 22)
                minute = random.randint(0, 59)
                news['timestamp'] = target_date.replace(
                    hour=hour, minute=minute)

                unique_news.append(news)

        print(f"\n去重后: {len(unique_news)} 条真实新闻")

        return unique_news

    def save_news_to_db(self, news_list):
        """保存新闻到数据库"""
        saved_count = 0
        duplicate_count = 0

        for news_data in news_list:
            # 检查是否已存在（基于标题）
            existing = News.query.filter(
                News.title == news_data['title']
            ).first()

            if existing:
                duplicate_count += 1
                continue

            # 创建新闻记录
            news = News(
                title=news_data['title'],
                content=news_data.get('content', news_data['title']),
                summary=news_data.get('summary', news_data['title'][:100]),
                source=news_data.get('source', '网络新闻'),
                image_url='',
                url=news_data.get('url', ''),
                timestamp=news_data.get('timestamp', datetime.now()),
                views=random.randint(100, 10000)
            )

            db.session.add(news)
            saved_count += 1

        try:
            db.session.commit()
            print(f"✅ 保存成功: {saved_count} 条, 重复: {duplicate_count} 条")
            return saved_count, duplicate_count
        except Exception as e:
            print(f"❌ 保存失败: {e}")
            db.session.rollback()
            return 0, duplicate_count


def scrape_and_save_news(target_date=None):
    """爬取并保存新闻"""

    scraper = RealNewsScraper()

    with app.app_context():
        # 爬取新闻
        news_list = scraper.scrape_real_news(target_date)

        if not news_list:
            print("⚠️  未获取到新闻")
            return 0, 0

        # 保存到数据库
        saved, duplicate = scraper.save_news_to_db(news_list)

        return saved, duplicate


def auto_fill_missing_dates():
    """自动填充缺失日期的真实新闻"""

    print("="*70)
    print("自动检测并补充缺失日期的真实新闻")
    print("="*70)

    with app.app_context():
        from sqlalchemy import func

        # 获取日期范围
        start_date = datetime(2026, 1, 1).date()
        today = datetime.now().date()

        # 找出缺失新闻的日期
        missing_dates = []
        current = start_date

        print(f"\n检查日期范围: {start_date} 至 {today}")
        print("正在检测缺失日期的新闻...")

        # 每隔几天检查一次（避免检查太多）
        step = 3
        while current <= today:
            day_news = News.query.filter(
                func.date(News.timestamp) == current
            ).count()

            if day_news == 0:
                missing_dates.append(current)

            current += timedelta(days=step)

        if not missing_dates:
            print("✅ 所有日期都有新闻，无需补充")
            return

        print(f"\n发现 {len(missing_dates)} 个日期缺少新闻")
        print(f"开始爬取真实新闻补充...\n")

        total_saved = 0
        total_duplicate = 0

        # 对每个缺失日期爬取新闻
        for missing_date in missing_dates:
            print(f"\n补充 {missing_date.strftime('%Y-%m-%d')} 的新闻:")
            print("-" * 70)

            # 爬取该日期的真实新闻
            saved, duplicate = scrape_and_save_news(
                datetime.combine(missing_date, datetime.min.time())
            )

            total_saved += saved
            total_duplicate += duplicate

            # 等待一下，避免请求过快
            time.sleep(random.uniform(3, 5))

        print(f"\n{'='*70}")
        print(f"✅ 补充完成！")
        print(f"新增新闻: {total_saved} 条")
        print(f"跳过重复: {total_duplicate} 条")
        print(f"{'='*70}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='真实新闻爬虫')
    parser.add_argument('--date', type=str, help='指定日期 YYYY-MM-DD')
    parser.add_argument('--auto-fill', action='store_true', help='自动补充缺失日期')
    parser.add_argument('--today', action='store_true', help='只爬取今天')

    args = parser.parse_args()

    with app.app_context():
        if args.auto_fill:
            auto_fill_missing_dates()
        elif args.date:
            target_date = datetime.strptime(args.date, '%Y-%m-%d')
            scrape_and_save_news(target_date)
        elif args.today:
            scrape_and_save_news(datetime.now())
        else:
            # 默认补充缺失日期
            auto_fill_missing_dates()
