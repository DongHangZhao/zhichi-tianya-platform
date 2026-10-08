'''
Author: your name
Date: 2026-04-11 23:16:58
LastEditTime: 2026-04-11 23:25:10
LastEditors: ZDH
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\init_trending.py
'''
# -*- coding: utf-8 -*-
"""
初始化热度排行表并填充数据
"""

import os
import sys
import math
from datetime import datetime, date
from models import Trending, Post, News, Video
from app import app, db

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def calculate_score(views, likes, comments, hours_old):
    """计算热度分数"""
    base_score = (likes * 1.0) + (comments * 2.0) + (views * 0.1)
    time_decay = math.log(hours_old + 2)
    final_score = base_score / time_decay
    return round(final_score, 2)


def init_and_fill_trending():
    """初始化并填充热度排行"""

    print("="*70)
    print("初始化热度排行表")
    print("="*70)

    with app.app_context():
        # 创建表
        print("\n创建trending表...")
        db.create_all()
        print("表已创建")

        # 清空旧数据
        print("\n清空旧数据...")
        Trending.query.delete()
        db.session.commit()

        now = datetime.now()

        # 计算动态热度
        print("\n[1/3] 计算动态热度...")
        posts = Post.query.all()
        post_count = 0

        for post in posts:
            hours_old = max(1, (now - post.timestamp).total_seconds() / 3600)
            score = calculate_score(
                0, post.likes_count or 0, post.comments_count or 0, hours_old)

            trending = Trending(
                item_type='post',
                item_id=post.id,
                score=score,
                date=date.today()
            )
            db.session.add(trending)
            post_count += 1

        print(f"  动态: {post_count} 条")

        # 计算新闻热度
        print("\n[2/3] 计算新闻热度...")
        news_list = News.query.all()
        news_count = 0

        for news in news_list:
            hours_old = max(1, (now - news.timestamp).total_seconds() / 3600)
            score = calculate_score(
                news.views or 0, news.likes_count or 0, news.comments_count or 0, hours_old)

            trending = Trending(
                item_type='news',
                item_id=news.id,
                score=score,
                date=date.today()
            )
            db.session.add(trending)
            news_count += 1

        print(f"  新闻: {news_count} 条")

        # 计算视频热度
        print("\n[3/3] 计算视频热度...")
        videos = Video.query.all()
        video_count = 0

        for video in videos:
            hours_old = max(1, (now - video.timestamp).total_seconds() / 3600)
            score = calculate_score(
                video.views or 0, video.likes_count or 0, 0, hours_old)

            trending = Trending(
                item_type='video',
                item_id=video.id,
                score=score,
                date=date.today()
            )
            db.session.add(trending)
            video_count += 1

        print(f"  视频: {video_count} 条")

        # 提交
        try:
            db.session.commit()
            total = post_count + news_count + video_count

            print(f"\n{'='*70}")
            print(f"热度排行初始化完成！")
            print(f"总计: {total} 条")
            print(f"{'='*70}")

            # 显示TOP 10
            top_items = Trending.query.order_by(
                Trending.score.desc()).limit(10).all()
            print(f"\n热度TOP 10:")
            for i, item in enumerate(top_items, 1):
                print(
                    f"  {i}. {item.item_type} #{item.item_id} - 热度: {item.score}")

        except Exception as e:
            print(f"\n保存失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()


if __name__ == '__main__':
    init_and_fill_trending()
