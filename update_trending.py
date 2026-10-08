# -*- coding: utf-8 -*-
"""
计算并更新热度排行数据
基于点赞数、评论数、浏览数和时间衰减因子计算热度分数
"""

from models import Trending, Post, News, Video
from app import app, db
import sys
import os
import math
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def calculate_score(views, likes, comments, hours_old):
    """
    计算热度分数
    使用Reddit风格算法 + 时间衰减

    score = (点赞*1 + 评论*2 + 浏览*0.1) / (时间衰减)
    时间衰减：log(小时数+2)
    """
    # 基础分数
    base_score = (likes * 1.0) + (comments * 2.0) + (views * 0.1)

    # 时间衰减因子（越新的内容权重越高）
    time_decay = math.log(hours_old + 2)

    # 最终分数
    final_score = base_score / time_decay

    return round(final_score, 2)


def update_trending():
    """更新热度排行"""

    print("="*70)
    print("计算并更新热度排行")
    print("="*70)

    with app.app_context():
        now = datetime.now()
        total_added = 0

        # 清空旧数据
        print("\n清空旧的热度数据...")
        Trending.query.delete()
        db.session.commit()

        # 1. 计算动态热度
        print("\n[1/3] 计算动态热度...")
        posts = Post.query.all()
        post_count = 0

        for post in posts:
            hours_old = max(1, (now - post.timestamp).total_seconds() / 3600)
            score = calculate_score(
                0,
                post.likes_count or 0,
                post.comments_count or 0,
                hours_old
            )

            trending = Trending(
                item_type='post',
                item_id=post.id,
                score=score,
                date=now.date()
            )
            db.session.add(trending)
            post_count += 1

        print(f"  动态: {post_count} 条")

        # 2. 计算新闻热度
        print("\n[2/3] 计算新闻热度...")
        news_list = News.query.all()
        news_count = 0

        for news in news_list:
            hours_old = max(1, (now - news.timestamp).total_seconds() / 3600)
            score = calculate_score(
                news.views or 0,
                news.likes_count or 0,
                news.comments_count or 0,
                hours_old
            )

            trending = Trending(
                item_type='news',
                item_id=news.id,
                score=score,
                date=now.date()
            )
            db.session.add(trending)
            news_count += 1

        print(f"  新闻: {news_count} 条")

        # 3. 计算视频热度
        print("\n[3/3] 计算视频热度...")
        videos = Video.query.all()
        video_count = 0

        for video in videos:
            hours_old = max(1, (now - video.timestamp).total_seconds() / 3600)
            score = calculate_score(
                video.views or 0,
                video.likes_count or 0,
                0,
                hours_old
            )

            trending = Trending(
                item_type='video',
                item_id=video.id,
                score=score,
                date=now.date()
            )
            db.session.add(trending)
            video_count += 1

        print(f"  视频: {video_count} 条")

        # 提交
        try:
            db.session.commit()
            total_added = post_count + news_count + video_count

            print(f"\n{'='*70}")
            print(f"热度排行更新完成！")
            print(f"总计: {total_added} 条")
            print(f"  - 动态: {post_count} 条")
            print(f"  - 新闻: {news_count} 条")
            print(f"  - 视频: {video_count} 条")
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
            db.session.rollback()


if __name__ == '__main__':
    update_trending()
