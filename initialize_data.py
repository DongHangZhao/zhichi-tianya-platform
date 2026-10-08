"""
Author: your name
Date: 2026-01-10 13:46:00
LastEditTime: 2026-01-10 13:46:00
LastEditors: your name
Description: In User Settings Edit
FilePath: e:\\办公练习\\Html\\Q文件\\python_web_project\\initialize_data.py
"""

"""
咫尺天涯社交平台 - 数据初始化脚本
用于添加内置用户、新闻、视频等初始数据
"""

import sys
import os
from app import app, db
from models import User, Post, Video, News, Message
from utils import generate_avatar_color
import random
from utils.time_utils import get_current_time
from datetime import datetime, timedelta, timezone
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def initialize_users():
    """初始化内置用户"""
    print("正在创建内置用户...")

    # 内置用户数据
    users_data = [
        {'username': 'admin', 'email': 'admin@zhichi.com',
            'password': 'admin123', 'is_admin': True},
        {'username': 'zhangsan', 'email': 'zhangsan@zhichi.com',
            'password': 'password123'},
        {'username': 'lisi', 'email': 'lisi@zhichi.com', 'password': 'password123'},
        {'username': 'wangwu', 'email': 'wangwu@zhichi.com', 'password': 'password123'},
        {'username': 'zhaoliu', 'email': 'zhaoliu@zhichi.com',
            'password': 'password123'},
        {'username': 'tianmi', 'email': 'tianmi@zhichi.com', 'password': 'password123'},
        {'username': 'xiaoming', 'email': 'xiaoming@zhichi.com',
            'password': 'password123'},
        {'username': 'meimei', 'email': 'meimei@zhichi.com', 'password': 'password123'},
    ]

    for user_data in users_data:
        existing_user = User.query.filter_by(
            username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                is_admin=user_data.get('is_admin', False)
            )
            user.set_password(user_data['password'])
            user.avatar = f"avatars/default_avatar_{generate_avatar_color(user.username)[1:]}.png"
            user.bio = f"我是{user.username}，很高兴认识大家！"
            user.location = '中国'
            db.session.add(user)

    db.session.commit()
    print("✓ 内置用户创建完成")


def initialize_news():
    """初始化新闻数据"""
    print("正在创建新闻数据...")

    news_data = [
        {
            'title': '国家发展改革委：我国经济持续回升向好',
            'content': '国家发展改革委今天发布最新数据显示，我国经济运行总体平稳，主要指标持续回升向好，高质量发展扎实推进。',
            'summary': '经济运行总体平稳，主要指标持续回升向好',
            'source': '央视新闻',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(1, 24))
        },
        {
            'title': '科技部：人工智能技术发展取得重大突破',
            'content': '科技部今日宣布，我国在人工智能领域取得一系列重大突破，多项技术达到国际先进水平，为经济发展注入新动能。',
            'summary': '人工智能领域取得重大突破',
            'source': '新华社',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(2, 48))
        },
        {
            'title': '教育部：高等教育改革持续推进',
            'content': '教育部表示，将继续深化高等教育改革，提升人才培养质量，推动教育事业高质量发展。',
            'summary': '高等教育改革持续推进',
            'source': '人民日报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(3, 72))
        },
        {
            'title': '卫生健康委：医疗服务能力不断提升',
            'content': '国家卫生健康委表示，将持续提升医疗服务能力，优化医疗资源配置，更好保障人民健康权益。',
            'summary': '医疗服务能力不断提升',
            'source': '健康报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(4, 96))
        },
        {
            'title': '工信部：数字经济规模持续扩大',
            'content': '工业和信息化部发布报告称，我国数字经济规模持续扩大，成为经济增长的重要引擎。',
            'summary': '数字经济规模持续扩大',
            'source': '经济日报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(5, 120))
        },
        {
            'title': '农业农村部：粮食产量再创新高',
            'content': '农业农村部数据显示，全国粮食产量连续多年稳定增长，为经济社会发展奠定坚实基础。',
            'summary': '粮食产量再创新高',
            'source': '农民日报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(6, 144))
        },
        {
            'title': '生态环境部：环境质量持续改善',
            'content': '生态环境部通报，全国环境质量持续改善，美丽中国建设取得积极进展。',
            'summary': '环境质量持续改善',
            'source': '中国环境报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(7, 168))
        },
        {
            'title': '交通运输部：基础设施建设成效显著',
            'content': '交通运输部表示，我国交通基础设施建设成效显著，为经济社会发展提供有力支撑。',
            'summary': '基础设施建设成效显著',
            'source': '中国交通报',
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(8, 192))
        }
    ]

    for news_item in news_data:
        existing_news = News.query.filter_by(title=news_item['title']).first()
        if not existing_news:
            news = News(
                title=news_item['title'],
                content=news_item['content'],
                summary=news_item['summary'],
                source=news_item['source'],
                timestamp=news_item['timestamp']
            )
            db.session.add(news)

    db.session.commit()
    print("✓ 新闻数据创建完成")


def initialize_videos():
    """初始化视频数据"""
    print("正在创建视频数据...")

    video_data = [
        {
            'title': '科技前沿：AI如何改变世界',
            'description': '探讨人工智能技术如何改变我们的生活和工作方式',
            'duration': 1800,  # 30分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 2,  # zhangsan
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(1, 24)),
            'video_url': 'videos/sample_video_1.mp4',  # 虚拟路径，后续可替换为真实URL
            'thumbnail_url': 'https://via.placeholder.com/300x200/007bff/ffffff?text=AI+Video'  # 使用占位图
        },
        {
            'title': '美食探索：中华传统美食之旅',
            'description': '带您领略中华大地上的传统美食文化',
            'duration': 2400,  # 40分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 3,  # lisi
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(2, 48)),
            'video_url': 'videos/sample_video_2.mp4',
            'thumbnail_url': 'https://via.placeholder.com/300x200/28a745/ffffff?text=Food+Tour'
        },
        {
            'title': '旅行日记：最美风景在路上',
            'description': '记录旅途中的美景和感动瞬间',
            'duration': 1500,  # 25分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 4,  # wangwu
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(3, 72)),
            'video_url': 'videos/sample_video_3.mp4',
            'thumbnail_url': 'https://via.placeholder.com/300x200/dc3545/ffffff?text=Travel'
        },
        {
            'title': '音乐时光：经典老歌回顾',
            'description': '重温那些年我们一起听过的经典老歌',
            'duration': 3600,  # 60分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 5,  # zhaoliu
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(4, 96)),
            'video_url': 'videos/sample_video_4.mp4',
            'thumbnail_url': 'https://via.placeholder.com/300x200/ffc107/000000?text=Music'
        },
        {
            'title': '生活技巧：实用小窍门分享',
            'description': '分享生活中实用的小窍门和技巧',
            'duration': 1200,  # 20分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 6,  # tianmi
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(5, 120)),
            'video_url': 'videos/sample_video_5.mp4',
            'thumbnail_url': 'https://via.placeholder.com/300x200/17a2b8/ffffff?text=Lifestyle'
        },
        {
            'title': '健身指导：科学锻炼方法',
            'description': '专业教练指导科学的健身锻炼方法',
            'duration': 1800,  # 30分钟
            'views': random.randint(1000, 10000),
            'uploader_id': 7,  # xiaoming
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None) - timedelta(hours=random.randint(6, 144)),
            'video_url': 'videos/sample_video_6.mp4',
            'thumbnail_url': 'https://via.placeholder.com/300x200/6f42c1/ffffff?text=Fitness'
        }
    ]

    for video_item in video_data:
        video = Video(
            title=video_item['title'],
            description=video_item['description'],
            duration=video_item['duration'],
            views=video_item['views'],
            uploader_id=video_item['uploader_id'],
            timestamp=video_item['timestamp']
        )
        # 设置视频和缩略图URL
        video.video_url = video_item['video_url']
        video.thumbnail_url = video_item['thumbnail_url']
        db.session.add(video)

    db.session.commit()
    print("✓ 视频数据创建完成")


def create_follow_relationships():
    """创建用户间的关注关系"""
    print("正在创建用户关注关系...")

    # 获取所有用户
    users = User.query.all()

    # 创建一些固定的关注关系
    follow_pairs = [
        (2, 3),  # zhangsan 关注 lisi
        (2, 4),  # zhangsan 关注 wangwu
        (3, 2),  # lisi 关注 zhangsan
        (3, 5),  # lisi 关注 zhaoliu
        (4, 2),  # wangwu 关注 zhangsan
        (4, 3),  # wangwu 关注 lisi
        (5, 6),  # zhaoliu 关注 tianmi
        (6, 7),  # tianmi 关注 xiaoming
        (7, 8),  # xiaoming 关注 meimei
        (8, 5),  # meimei 关注 zhaoliu
    ]

    for follower_id, followed_id in follow_pairs:
        follower = User.query.get(follower_id)
        followed = User.query.get(followed_id)
        if follower and followed:
            # 检查是否已经关注，避免重复
            if not follower.is_following(followed):
                follower.follow(followed)

    db.session.commit()
    print("✓ 用户关注关系创建完成")


def initialize_posts():
    """初始化一些帖子数据"""
    print("正在创建帖子数据...")

    posts_data = [
        {
            'title': '今天天气真好，适合出门走走',
            'content': '阳光明媚的一天，心情也格外舒畅。大家今天有什么计划呢？',
            'author_id': 2
        },
        {
            'title': '分享一道家常菜的做法',
            'content': '今天做了一道红烧肉，味道很不错。先把肉焯水去腥，然后用冰糖炒糖色...',
            'author_id': 3
        },
        {
            'title': '最近看了部好电影推荐给大家',
            'content': '《流浪地球》真的是一部很棒的国产科幻片，特效做得非常棒，剧情也很感人。',
            'author_id': 4
        },
        {
            'title': '学习心得分享',
            'content': '最近在学习Python编程，感觉越来越有趣了。坚持就是胜利！',
            'author_id': 5
        },
        {
            'title': '周末出游计划',
            'content': '准备周末去郊外踏青，享受大自然的美好。有人一起吗？',
            'author_id': 6
        },
        {
            'title': '健身打卡',
            'content': '今天坚持运动一小时，身体感觉特别轻松。大家也要注意保持锻炼哦！',
            'author_id': 7
        },
        {
            'title': '读书感悟',
            'content': '最近在读《活着》，这本书让人深思生命的意义。强烈推荐给大家。',
            'author_id': 8
        }
    ]

    for post_data in posts_data:
        post = Post(
            title=post_data['title'],
            content=post_data['content'],
            author_id=post_data['author_id'],
            timestamp=get_current_time().astimezone(timezone.utc).replace(
                tzinfo=None) - timedelta(hours=random.randint(1, 168))
        )
        db.session.add(post)

    db.session.commit()
    print("✓ 帖子数据创建完成")


def main():
    """主函数"""
    print("开始初始化数据...")

    with app.app_context():
        # 创建所有表（如果不存在）
        db.create_all()

        # 执行各项初始化
        initialize_users()
        initialize_news()
        initialize_videos()
        initialize_posts()
        create_follow_relationships()

        print("\n🎉 数据初始化完成！")
        print("- 创建了8个内置用户（包括1个管理员）")
        print("- 添加了8条新闻数据")
        print("- 添加了6个视频数据")
        print("- 添加了7条帖子数据")
        print("- 创建了用户间的关注关系")
        print("\n内置用户账号：")
        print("  管理员: admin / admin123")
        print(
            "  普通用户: zhangsan/lisi/wangwu/zhaoliu/tianmi/xiaoming/meimei (密码: password123)")


if __name__ == "__main__":
    main()
