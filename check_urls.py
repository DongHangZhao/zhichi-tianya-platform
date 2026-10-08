'''
Author: your name
Date: 2026-04-11 22:46:47
LastEditTime: 2026-04-11 22:46:47
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\check_urls.py
'''
"""
验证新闻链接质量
"""

import os
import sys
from models import News
from app import app, db

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_url_quality():
    """检查URL质量"""

    with app.app_context():
        all_news = News.query.all()

        print("="*70)
        print("新闻链接质量检查")
        print("="*70)
        print(f"\n总新闻数: {len(all_news)}")

        with_url = []
        without_url = []

        for news in all_news:
            if news.url and news.url.startswith('http'):
                with_url.append(news)
            else:
                without_url.append(news)

        print(f"有真实链接: {len(with_url)}")
        print(f"无链接/假链接: {len(without_url)}")

        if without_url:
            print(f"\n⚠️  发现 {len(without_url)} 条没有真实链接的新闻:")
            for i, news in enumerate(without_url, 1):
                print(f"  {i}. {news.title[:60]}")
                print(f"     URL: {news.url or '(空)'}")

        print(f"\n{'='*70}")
        print("链接来源分布:")
        print(f"{'='*70}")

        sources = {}
        for news in with_url:
            source = news.source or '未知'
            if source not in sources:
                sources[source] = 0
            sources[source] += 1

        for source, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"  {source}: {count} 条")

        print(f"\n{'='*70}")
        print("前10条新闻示例:")
        print(f"{'='*70}")

        for i, news in enumerate(with_url[:10], 1):
            print(f"\n{i}. {news.title[:60]}")
            print(f"   来源: {news.source}")
            print(f"   URL: {news.url}")

        print(f"\n{'='*70}")
        if len(without_url) == 0:
            print("✅ 所有新闻都有真实链接！")
        else:
            print(f"⚠️  需要修复 {len(without_url)} 条新闻")
        print(f"{'='*70}")


if __name__ == '__main__':
    check_url_quality()
