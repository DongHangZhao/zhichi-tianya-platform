"""
热度排行榜计算脚本
根据爱心、查看量、留言数综合排名娱乐花边消息
"""
import schedule
import time
from datetime import datetime, timedelta, date, timezone
from utils.time_utils import get_current_time
from app import app, db
from models import News, Trending, NewsLike, Comment, Post, Video
from chinese_time_utils import calculate_trend_score


def calculate_daily_trending():
    """
    计算每日热度排行榜
    """
    print(f"[{datetime.now()}] 开始计算每日热度排行榜...")

    with app.app_context():
        # 获取今天的所有内容
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())

        # 清除今天已有的热度记录
        Trending.query.filter(Trending.date == today).delete()

        trending_items = []

        # 计算新闻的热度
        todays_news = News.query.filter(
            News.timestamp >= start_of_day,
            News.timestamp <= end_of_day
        ).all()

        for news in todays_news:
            # 计算热度分数（基于喜欢数、查看数、评论数）
            likes_count = len(news.likes)  # 使用关系获取点赞数
            views_count = news.views
            comments_count = len(news.news_comments)  # 使用关系获取评论数

            # 计算内容年龄（小时）
            age = get_current_time().astimezone(
                timezone.utc).replace(tzinfo=None) - news.timestamp
            age_hours = age.total_seconds() / 3600

            # 使用热度算法计算分数
            score = calculate_trend_score(
                likes_count, views_count, comments_count, age_hours)

            # 创建热度记录
            trending_item = Trending(
                item_id=news.id,
                item_type='news',
                score=score,
                date=today
            )
            db.session.add(trending_item)
            trending_items.append({
                'item': news,
                'type': 'news',
                'score': score
            })

        # 计算帖子的热度
        todays_posts = Post.query.filter(
            Post.timestamp >= start_of_day,
            Post.timestamp <= end_of_day
        ).all()

        for post in todays_posts:
            likes_count = post.likes_count
            views_count = getattr(post, 'views', 0) or 0  # 帖子可能没有专门的views字段
            comments_count = post.comments_count

            # 计算内容年龄（小时）
            age = get_current_time().astimezone(
                timezone.utc).replace(tzinfo=None) - post.timestamp
            age_hours = age.total_seconds() / 3600

            # 使用热度算法计算分数
            score = calculate_trend_score(
                likes_count, views_count, comments_count, age_hours)

            # 创建热度记录
            trending_item = Trending(
                item_id=post.id,
                item_type='post',
                score=score,
                date=today
            )
            db.session.add(trending_item)
            trending_items.append({
                'item': post,
                'type': 'post',
                'score': score
            })

        # 计算视频的热度
        todays_videos = Video.query.filter(
            Video.timestamp >= start_of_day,
            Video.timestamp <= end_of_day
        ).all()

        for video in todays_videos:
            likes_count = video.likes_count
            views_count = video.views
            comments_count = video.comments_count

            # 计算内容年龄（小时）
            age = get_current_time().astimezone(
                timezone.utc).replace(tzinfo=None) - video.timestamp
            age_hours = age.total_seconds() / 3600

            # 使用热度算法计算分数
            score = calculate_trend_score(
                likes_count, views_count, comments_count, age_hours)

            # 创建热度记录
            trending_item = Trending(
                item_id=video.id,
                item_type='video',
                score=score,
                date=today
            )
            db.session.add(trending_item)
            trending_items.append({
                'item': video,
                'type': 'video',
                'score': score
            })

        # 按分数排序并保存
        trending_items.sort(key=lambda x: x['score'], reverse=True)

        try:
            db.session.commit()
            print(f"[{datetime.now()}] 成功计算了 {len(trending_items)} 个热度项目")
        except Exception as e:
            print(f"[{datetime.now()}] 计算热度排行榜时出错: {e}")
            db.session.rollback()


def calculate_and_save_trending_scores():
    """
    计算并保存热度分数（兼容函数名）
    """
    calculate_daily_trending()


def schedule_trending_updates():
    """
    设置热度排行榜更新任务
    """
    # 每天晚上10点更新热度排行榜
    schedule.every().day.at("22:00").do(calculate_daily_trending)

    print("已设置每日热度排行榜更新任务，每天晚上10点执行")

    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    # 立即执行一次计算作为测试
    with app.app_context():
        calculate_daily_trending()

    # 启动定时任务
    # schedule_trending_updates()
