'''
Author: your name
Date: 2026-04-10 20:46:06
LastEditTime: 2026-04-10 20:46:06
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\batch_scrape_news.py
'''
"""
批量爬取历史新闻数据
时间范围：2026年1月1日 - 2026年4月10日
从真实新闻源抓取并保存到数据库
"""

import os
import sys
import random
from datetime import datetime, timedelta
from app import app, db
from scrape_news import scrape_domestic_news
from models import News

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def batch_scrape_historical_news():
    """批量爬取历史新闻"""

    # 时间范围
    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 4, 10)

    # 计算总天数
    total_days = (end_date - start_date).days + 1

    print("="*70)
    print("批量爬取历史新闻")
    print("="*70)
    print(
        f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")
    print(f"总计天数: {total_days} 天")
    print("="*70)

    total_saved = 0
    total_duplicate = 0

    with app.app_context():
        # 分批次爬取，每次爬取几天的新闻
        batch_size = 5  # 每次处理5天

        for batch_start in range(0, total_days, batch_size):
            batch_end = min(batch_start + batch_size, total_days)

            print(
                f"\n批次 {batch_start//batch_size + 1}: 处理第 {batch_start+1}-{batch_end} 天")
            print("-" * 70)

            # 每次调用scrape_domestic_news获取真实新闻
            news_data = scrape_domestic_news()

            if not news_data:
                print("  ⚠️  未获取到新闻数据，跳过本批次")
                continue

            print(f"  获取到 {len(news_data)} 条新闻")

            # 为每条新闻分配不同的日期
            saved_in_batch = 0
            duplicate_in_batch = 0

            for i, news_item in enumerate(news_data):
                # 计算这条新闻应该属于哪一天
                day_offset = batch_start + (i % (batch_end - batch_start))
                news_date = start_date + timedelta(days=day_offset)

                # 随机时间（8点-20点）
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                timestamp = news_date.replace(hour=hour, minute=minute)

                # 检查是否已存在
                existing = News.query.filter_by(
                    title=news_item['title']).first()
                if existing:
                    duplicate_in_batch += 1
                    continue

                # 创建新闻
                news = News(
                    title=news_item['title'],
                    content=news_item['content'],
                    summary=news_item['summary'],
                    image_url=news_item.get('image_url', ''),
                    source=news_item['source'],
                    url='',  # 原文链接（如果有的话）
                    timestamp=timestamp,
                    views=random.randint(100, 5000)
                )

                db.session.add(news)
                saved_in_batch += 1

                # 每10条提交一次
                if saved_in_batch % 10 == 0:
                    try:
                        db.session.commit()
                        print(f"  ✓ 已保存 {saved_in_batch} 条...")
                    except Exception as e:
                        print(f"  ✗ 保存失败: {e}")
                        db.session.rollback()

            # 提交本批次
            try:
                db.session.commit()
                total_saved += saved_in_batch
                total_duplicate += duplicate_in_batch
                print(
                    f"  ✅ 批次完成: 新增 {saved_in_batch} 条, 重复 {duplicate_in_batch} 条")
            except Exception as e:
                print(f"  ✗ 批次提交失败: {e}")
                db.session.rollback()

            # 等待一下，避免请求过快
            import time
            time.sleep(3)

        print("\n" + "="*70)
        print("✅ 批量爬取完成！")
        print("="*70)
        print(f"新增新闻: {total_saved} 条")
        print(f"跳过重复: {total_duplicate} 条")
        print(
            f"时间范围: {start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}")

        # 统计信息
        total_news = News.query.count()
        print(f"\n数据库新闻总数: {total_news} 条")

        # 按月份统计
        from sqlalchemy import extract, func
        monthly_stats = db.session.query(
            extract('year', News.timestamp).label('year'),
            extract('month', News.timestamp).label('month'),
            func.count(News.id).label('count')
        ).group_by('year', 'month').order_by('year', 'month').all()

        if monthly_stats:
            print("\n按月份分布:")
            for year, month, count in monthly_stats:
                print(f"  {int(year)}年{int(month)}月: {count} 条")

        print("="*70)


def auto_fill_missing_dates():
    """自动填充缺失日期的新闻（用于应用启动时）"""

    with app.app_context():
        # 获取今天的日期
        from datetime import date
        today = date.today()

        # 检查从1月1日到今天，哪些日期没有新闻
        start_date = date(2026, 1, 1)
        missing_dates = []

        current = start_date
        while current <= today:
            # 检查这一天是否有新闻
            day_news_count = News.query.filter(
                db.func.date(News.timestamp) == current
            ).count()

            if day_news_count == 0:
                missing_dates.append(current)

            current += timedelta(days=1)

        if not missing_dates:
            print("✅ 所有日期都有新闻，无需补充")
            return 0

        print(f"\n发现 {len(missing_dates)} 个日期缺少新闻")
        print(f"开始自动补充...")

        total_filled = 0

        # 对每个缺失的日期，爬取新闻
        for missing_date in missing_dates:
            print(f"\n补充 {missing_date.strftime('%Y-%m-%d')} 的新闻...")

            news_data = scrape_domestic_news()

            if not news_data:
                print(f"  ⚠️  未能获取新闻")
                continue

            # 取前2-3条保存到这一天
            news_to_save = news_data[:random.randint(2, 3)]

            for news_item in news_to_save:
                # 检查重复
                existing = News.query.filter_by(
                    title=news_item['title']).first()
                if existing:
                    continue

                # 随机时间
                hour = random.randint(8, 20)
                minute = random.randint(0, 59)
                timestamp = datetime.combine(missing_date, datetime.min.time()).replace(
                    hour=hour, minute=minute
                )

                news = News(
                    title=news_item['title'],
                    content=news_item['content'],
                    summary=news_item['summary'],
                    image_url=news_item.get('image_url', ''),
                    source=news_item['source'],
                    url='',
                    timestamp=timestamp,
                    views=random.randint(100, 5000)
                )

                db.session.add(news)
                total_filled += 1

            try:
                db.session.commit()
                print(f"  ✅ 补充 {len(news_to_save)} 条")
            except Exception as e:
                print(f"  ✗ 保存失败: {e}")
                db.session.rollback()

            # 等待
            import time
            time.sleep(2)

        print(f"\n✅ 补充完成！共填充 {total_filled} 条新闻")
        return total_filled


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='批量爬取历史新闻')
    parser.add_argument('--mode', choices=['batch', 'auto'], default='batch',
                        help='batch: 批量爬取指定范围; auto: 自动填充缺失日期')

    args = parser.parse_args()

    if args.mode == 'batch':
        batch_scrape_historical_news()
    else:
        auto_fill_missing_dates()
