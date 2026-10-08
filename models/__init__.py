'''
Author: your name
Date: 2026-01-10 13:21:56
LastEditTime: 2026-01-10 13:21:56
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\models\__init__.py
'''
"""
咫尺天涯社交平台 - 数据库模型
包含用户、帖子、视频、消息等所有数据模型
"""

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pytz
from datetime import datetime, timezone
from sqlalchemy.types import TypeDecorator, DateTime
import json

db = SQLAlchemy()


class FlexibleDateTime(TypeDecorator):
    """
    自定义灵活的日期时间类型，能处理多种时间戳格式
    """
    impl = DateTime
    cache_ok = True  # 添加缓存标识

    def process_bind_param(self, value, dialect):
        return value

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return datetime.now()  # 使用本地时间
        if isinstance(value, str):
            # 处理不同格式的时间戳字符串
            if value.strip() == '':
                return datetime.now()  # 使用本地时间
            # 尝试解析标准格式
            try:
                # 处理包含毫秒的标准格式: 'YYYY-MM-DD HH:MM:SS.ffffff'
                if '.' in value:
                    # 分离秒和微秒部分
                    parts = value.split('.')
                    dt_part = parts[0]
                    microsec_part = parts[1][:6] if len(
                        parts) > 1 else '0'  # 限制微秒为6位

                    # 解析日期时间部分
                    dt = datetime.strptime(dt_part, '%Y-%m-%d %H:%M:%S')
                    # 添加微秒
                    return dt.replace(microsecond=int(microsec_part.ljust(6, '0')))
                else:
                    # 解析不含微秒的格式
                    return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                try:
                    # 尝试ISO格式
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        # 尝试其他常见格式
                        return datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # 如果都无法解析，返回当前本地时间
                        return datetime.now()  # 使用本地时间
        elif isinstance(value, (int, float)):
            # 如果是数字时间戳，转换为 datetime
            try:
                return datetime.fromtimestamp(value)
            except (ValueError, OSError):
                return datetime.now()  # 使用本地时间
        return value


class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.Text, default='')
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)  # 用户是否被封禁
    is_banned = db.Column(db.Boolean, default=False)  # 是否被完全封禁
    can_post = db.Column(db.Boolean, default=True)    # 是否可以发帖
    can_video = db.Column(db.Boolean, default=True)   # 是否可以发视频
    can_comment = db.Column(db.Boolean, default=True)  # 是否可以评论
    is_admin = db.Column(db.Boolean, default=False)   # 是否为管理员
    join_date = db.Column(FlexibleDateTime, default=datetime.now)
    last_seen = db.Column(FlexibleDateTime, default=datetime.now)

    # 关系
    posts = db.relationship('Post', backref='author',
                            lazy=True, foreign_keys='Post.author_id')
    videos = db.relationship('Video', backref='uploader',
                             lazy=True, foreign_keys='Video.uploader_id')
    comments = db.relationship(
        'Comment', lazy=True, foreign_keys='Comment.author_id')
    sent_messages = db.relationship(
        'Message', backref='sender', lazy=True, foreign_keys='Message.sender_id')
    received_messages = db.relationship(
        'Message', backref='recipient', lazy=True, foreign_keys='Message.recipient_id')
    followers = db.relationship(
        'User', secondary='follows',
        primaryjoin='(Follows.followed_id == User.id)',  # 被关注的人
        secondaryjoin='(Follows.follower_id == User.id)',  # 关注者
        backref=db.backref('followed', lazy='dynamic'),
        lazy='dynamic'
    )

    # 点赞关系
    post_likes = db.relationship('PostLike', backref='user', lazy=True)
    video_likes = db.relationship('VideoLike', backref='user', lazy=True)
    # news_likes已经在NewsLike模型中定义了，避免重复定义

    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        """关注用户"""
        # 使用原生SQL查询检查是否已经关注，避免autoflush问题
        existing_follow = db.session.query(Follows).filter_by(
            follower_id=self.id,
            followed_id=user.id
        ).first()

        if not existing_follow:
            f = Follows(follower_id=self.id, followed_id=user.id)
            db.session.add(f)

    def unfollow(self, user):
        """取消关注"""
        f = Follows.query.filter_by(
            follower_id=self.id, followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def followed_by_count(self):
        """获取被关注数（粉丝数）"""
        return self.followers.count()

    def following_count(self):
        """获取关注数"""
        return self.followed.count()

    def unfollow(self, user):
        """取消关注"""
        f = Follows.query.filter_by(
            follower_id=self.id, followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """检查是否关注了指定用户"""
        # 使用原生SQL查询，避免autoflush问题
        existing_follow = db.session.query(Follows).filter_by(
            follower_id=self.id,
            followed_id=user.id
        ).first()
        return existing_follow is not None

    def get_following_count(self):
        """获取关注数"""
        return self.followed.count()

    def get_followers_count(self):
        """获取粉丝数"""
        return self.followers.count()

    def __repr__(self):
        return f'<User {self.username}>'

    def unread_messages_count(self):
        """获取未读消息数量"""
        return Message.query.filter_by(
            recipient_id=self.id,
            is_read=False
        ).count()

    def get_unread_notifications(self):
        """获取未读通知"""
        return Message.query.filter_by(
            recipient_id=self.id,
            is_read=False,
            message_type='notification'
        ).order_by(Message.timestamp.desc()).all()

    def get_unread_warnings(self):
        """获取未读警告"""
        return Message.query.filter_by(
            recipient_id=self.id,
            is_read=False,
            message_type='warning'
        ).order_by(Message.timestamp.desc()).all()

    def liked_news_ids(self):
        """获取用户点赞的新闻ID列表"""
        return [like.news_id for like in self.get_news_likes()]

    def get_news_likes(self):
        """获取用户点赞的新闻"""
        return NewsLike.query.filter_by(user_id=self.id).all()


class UserStatus(db.Model):
    """用户在线状态模型"""
    __tablename__ = 'user_status'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_online = db.Column(db.Boolean, default=False)  # 当前在线状态
    last_online_time = db.Column(FlexibleDateTime)  # 最后上线时间
    last_offline_time = db.Column(FlexibleDateTime)  # 最后下线时间
    created_at = db.Column(FlexibleDateTime, default=datetime.now)
    updated_at = db.Column(
        FlexibleDateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    user = db.relationship('User', backref=db.backref(
        'status', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<UserStatus {self.user_id} - Online: {self.is_online}>'


class Follows(db.Model):
    """关注关系模型"""
    __tablename__ = 'follows'

    follower_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)


class Post(db.Model):
    """帖子模型"""
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200))  # 帖子配图
    video_url = db.Column(db.String(200))  # 帖子视频
    timestamp = db.Column(FlexibleDateTime, index=True,
                          default=datetime.now)
    updated_at = db.Column(FlexibleDateTime, default=datetime.now)  # 最后更新时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)

    # 关系
    post_comments = db.relationship(
        'Comment', lazy=True, foreign_keys='Comment.post_id')
    likes = db.relationship('PostLike', backref='post', lazy=True)

    def get_liking_users(self):
        """获取点赞用户"""
        return [like.user for like in self.likes]

    def is_liked_by(self, user):
        """检查用户是否点赞了此帖子"""
        return PostLike.query.filter_by(post_id=self.id, user_id=user.id).count() > 0

    def update_content(self, field_name, old_value, new_value, user):
        """更新内容并记录历史"""
        setattr(self, field_name, new_value)
        self.updated_at = datetime.utcnow()

        # 创建历史记录
        history = ContentHistory(
            content_type='post',
            content_id=self.id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            user_id=user.id
        )
        db.session.add(history)


class PostLike(db.Model):
    """帖子点赞模型"""
    __tablename__ = 'post_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)

    # 确保一个用户只能对一个帖子点赞一次
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id'),)


class Video(db.Model):
    """视频模型"""
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(200), nullable=False)  # 视频文件路径
    thumbnail_url = db.Column(db.String(200))  # 缩略图
    duration = db.Column(db.Integer)  # 视频时长（秒）
    views = db.Column(db.Integer, default=0)  # 观看次数
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    timestamp = db.Column(FlexibleDateTime, index=True,
                          default=datetime.now)
    updated_at = db.Column(FlexibleDateTime, default=datetime.now)  # 最后更新时间
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关系
    video_comments = db.relationship(
        'Comment', lazy=True, foreign_keys='Comment.video_id')
    likes = db.relationship('VideoLike', backref='video', lazy=True)

    def update_content(self, field_name, old_value, new_value, user):
        """更新内容并记录历史"""
        setattr(self, field_name, new_value)
        self.updated_at = datetime.now()  # 使用本地时间

        # 创建历史记录
        history = ContentHistory(
            content_type='video',
            content_id=self.id,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            user_id=user.id
        )
        db.session.add(history)


class VideoLike(db.Model):
    """视频点赞模型"""
    __tablename__ = 'video_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    video_id = db.Column(db.Integer, db.ForeignKey(
        'videos.id'), nullable=False)
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)

    # 确保一个用户只能对一个视频点赞一次
    __table_args__ = (db.UniqueConstraint('user_id', 'video_id'),)


class Comment(db.Model):
    """评论模型"""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(FlexibleDateTime, index=True,
                          default=datetime.now)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # 关联到帖子、视频或新闻（使用polymorphic关联）
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'))
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'))  # 添加新闻关联

    # 点赞
    likes_count = db.Column(db.Integer, default=0)

    # 关系
    author = db.relationship('User', overlaps="comments,user_comments")
    post = db.relationship('Post', overlaps="post_comments")
    video = db.relationship('Video', overlaps="video_comments")
    news = db.relationship('News', overlaps="news_comments")


class Message(db.Model):
    """私信模型"""
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(FlexibleDateTime, index=True,
                          default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    # 'message', 'notification', 'warning'
    message_type = db.Column(db.String(20), default='message')
    related_id = db.Column(db.Integer)  # 关联的ID（如帖子ID、视频ID等）
    related_type = db.Column(db.String(20))  # 关联类型（如'post', 'video'等）
    attachment_path = db.Column(db.String(500))  # 附件文件路径
    attachment_type = db.Column(db.String(50))  # 附件类型 (image, file, video等)
    attachment_filename = db.Column(db.String(200))  # 附件原始文件名
    updated_at = db.Column(FlexibleDateTime)  # 消息更新时间


class News(db.Model):
    """新闻模型"""
    __tablename__ = 'news'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.String(500))  # 新闻摘要
    image_url = db.Column(db.String(200))  # 新闻配图
    source = db.Column(db.String(100))  # 新闻来源
    url = db.Column(db.String(500), default='')  # 原文链接
    timestamp = db.Column(FlexibleDateTime, index=True,
                          default=datetime.now)
    views = db.Column(db.Integer, default=0)  # 阅读次数
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)  # 评论数

    # 关系
    news_likes_rel = db.relationship(
        'NewsLike', back_populates='news', overlaps="likes")
    news_comments = db.relationship(
        'Comment', lazy=True, foreign_keys='Comment.news_id')

    def get_liking_users(self):
        """获取点赞用户"""
        # 直接查询关联的用户
        likes = NewsLike.query.filter_by(news_id=self.id).all()
        user_ids = [like.user_id for like in likes]
        return User.query.filter(User.id.in_(user_ids)).all() if user_ids else []

    def is_liked_by(self, user):
        """检查用户是否点赞了此新闻"""
        return NewsLike.query.filter_by(news_id=self.id, user_id=user.id).count() > 0

    def get_trending_score(self):
        """获取热度分数"""
        from chinese_time_utils import calculate_trend_score
        from datetime import datetime
        import math

        # 计算内容年龄（小时）
        age = datetime.now() - self.timestamp
        age_hours = age.total_seconds() / 3600

        # 计算热度分数
        score = calculate_trend_score(
            self.likes_count,
            self.views,
            len(self.news_comments),
            age_hours
        )

        return score


class NewsLike(db.Model):
    """新闻点赞模型"""
    __tablename__ = 'news_likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)

    # 确保一个用户只能对一个新闻点赞一次
    __table_args__ = (db.UniqueConstraint('user_id', 'news_id'),)

    # 添加与User模型的关系
    user = db.relationship('User', backref='news_likes')
    # 添加与 News 模型的关系
    news = db.relationship(
        'News', back_populates='news_likes_rel', overlaps="news_likes_rel")


class NewsOperationLog(db.Model):
    """新闻操作日志模型 - 记录所有对新闻的操作"""
    __tablename__ = 'news_operation_logs'

    id = db.Column(db.Integer, primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # 'view', 'like', 'unlike', 'comment'
    operation_type = db.Column(db.String(20), nullable=False)
    old_value = db.Column(db.Integer)  # 操作前的值
    new_value = db.Column(db.Integer)  # 操作后的值
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)
    ip_address = db.Column(db.String(50))  # IP 地址
    user_agent = db.Column(db.String(200))  # 用户代理

    # 关系
    news = db.relationship('News', backref='operation_logs')
    user = db.relationship('User', backref='news_operations')

    def __repr__(self):
        return f'<NewsOperationLog {self.operation_type} on News {self.news_id} by User {self.user_id}>'


class Trending(db.Model):
    """热度排行模型"""
    __tablename__ = 'trending'

    id = db.Column(db.Integer, primary_key=True)
    # 'post', 'video', 'news'
    item_type = db.Column(db.String(20), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)  # 关联的项目ID
    score = db.Column(db.Float, default=0.0)  # 热度分数
    date = db.Column(db.Date, default=datetime.now)

    def __repr__(self):
        return f'<Trending {self.item_type}:{self.item_id} - Score:{self.score}>'


class ContentHistory(db.Model):
    """内容修改历史模型"""
    __tablename__ = 'content_history'

    id = db.Column(db.Integer, primary_key=True)
    content_type = db.Column(db.String(20), nullable=False)  # 'post', 'video'
    content_id = db.Column(db.Integer, nullable=False)       # 关联的内容ID
    field_name = db.Column(db.String(50), nullable=False)    # 修改的字段名
    old_value = db.Column(db.Text)                           # 修改前的值
    new_value = db.Column(db.Text)                           # 修改后的值
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)  # 修改时间
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))    # 修改用户

    # 关系 - 使用条件关系，因为一个历史记录可能关联到帖子或视频
    user = db.relationship('User', backref='content_histories')

    def __repr__(self):
        return f'<ContentHistory {self.content_type}:{self.content_id} - {self.field_name}>'



class PasswordResetRequest(db.Model):
    """密码重置请求模型"""
    __tablename__ = 'password_reset_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)  # 6位验证码
    created_at = db.Column(FlexibleDateTime, default=datetime.now)
    expires_at = db.Column(FlexibleDateTime, nullable=False)  # 过期时间
    is_used = db.Column(db.Boolean, default=False)  # 是否已使用
    used_at = db.Column(FlexibleDateTime)  # 使用时间
    
    # 关系
    user = db.relationship('User', backref=db.backref('reset_requests', lazy=True))
    
    def is_valid(self):
        """检查验证码是否有效"""
        return not self.is_used and datetime.now() < self.expires_at
    
    def __repr__(self):
        return f'<PasswordResetRequest User:{self.user_id} Code:{self.verification_code}>'


class PasswordChangeLog(db.Model):
    """密码修改日志模型"""
    __tablename__ = 'password_change_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_by = db.Column(db.String(50))  # 'user', 'admin', 'system'
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)
    reason = db.Column(db.String(200))  # 修改原因
    
    # 关系
    user = db.relationship('User', backref=db.backref('password_logs', lazy=True))
    
    def __repr__(self):
        return f'<PasswordChangeLog User:{self.user_id} By:{self.changed_by}>'

