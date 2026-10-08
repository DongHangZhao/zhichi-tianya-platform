'''
Author: your name
Date: 2026-01-20 23:08:00
LastEditTime: 2026-04-01 18:27:40
LastEditors: ZDH
Description: In User Settings Edit
FilePath: /Q文件/python_web_project/complete_app.py
'''
'''
Author: your name
Date: 2026-01-20 22:17:58
LastEditTime: 2026-01-20 22:29:33
LastEditors: ZDH
Description: In User Settings Edit
FilePath: /Q文件/python_web_project/app_clean.py
'''
# -*- coding: utf-8 -*-
"""
Flask Web Application for Social Platform
"""

from routes.password_routes import password_bp
from models import db, User, Post, Video, Comment, Message, News, PostLike, VideoLike, NewsLike, Trending, Follows, UserStatus, ContentHistory, NewsOperationLog
from admin_panel import init_admin
from routes.news import news_bp
from routes.delete import delete_bp
from collections import defaultdict
from werkzeug.utils import secure_filename
from flask import Response, session, render_template, request, jsonify, redirect, url_for, flash, send_file
import threading
from queue import Queue
import json
import os
from utils import save_image, save_file, calculate_trend_score, generate_avatar_color, generate_filename
from utils.time_utils import get_current_time, format_datetime_local, format_datetime_china_friendly
from forms import LoginForm, RegistrationForm, ProfileForm, PostForm, VideoForm, MessageForm, NewsForm, AdminUserBanForm, CommentForm
from config import config
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import time
from datetime import datetime, timedelta, timezone
import sqlite3
from scheduler import init_scheduler


# 根据环境变量选择配置
config_name = os.environ.get('FLASK_ENV', 'default')
app = Flask(__name__)
app.config.from_object(config[config_name])

# 用于存储SSE连接的队列

# 注册admin静态文件路由


@app.route('/static/admin/<path:filename>')
def admin_static(filename):
    """服务admin静态文件"""
    import os
    admin_static_path = os.path.join(
        app.template_folder, 'admin', 'static', filename)
    if os.path.exists(admin_static_path):
        return send_file(admin_static_path)
    return '', 404


user_connections = defaultdict(list)


@app.route('/events')
@login_required
def events():
    """SSE端点，用于推送实时更新"""
    def event_stream():
        # 检查用户是否仍然有效
        if not current_user or not current_user.is_authenticated:
            return

        user_id = current_user.id  # 提前获取用户ID，防止会话变化

        # 为当前用户创建队列
        user_queue = Queue()
        user_connections[user_id].append(user_queue)

        try:
            while True:
                # 检查用户是否仍然有效
                if not current_user or not current_user.is_authenticated:
                    break

                # 等待消息
                message = user_queue.get(timeout=30)  # 30秒超时
                yield f"data: {json.dumps(message)}\n\n"
        except Exception as e:
            print(f"SSE连接异常: {e}")
            return
        finally:
            # 清理连接
            if user_id in user_connections:
                try:
                    user_connections[user_id].remove(user_queue)
                    if not user_connections[user_id]:
                        del user_connections[user_id]
                except ValueError:
                    pass

    # 设置适当的SSE头部
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Connection'] = 'keep-alive'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


def notify_user_status_change(user_id, status_data):
    """通知指定用户的连接有关状态变更的信息"""
    if user_id in user_connections:
        message = {
            'type': 'status_update',
            'user_id': user_id,
            'data': status_data,
            'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None).isoformat()
        }

        # 向所有连接广播消息
        for queue in user_connections[user_id]:
            queue.put(message)


def notify_friends_about_status_change(current_user_id, status_data):
    """通知当前用户的所有好友关于状态变更的信息"""
    # 获取当前用户关注的所有用户
    user = User.query.get(current_user_id)
    if user:
        for friend in user.followed:
            if friend.id in user_connections:
                message = {
                    'type': 'friend_status_update',
                    'friend_id': current_user_id,
                    'data': status_data,
                    'timestamp': get_current_time().astimezone(timezone.utc).replace(tzinfo=None).isoformat()
                }

                # 向好友的所有连接广播消息
                for queue in user_connections[friend.id]:
                    queue.put(message)


# 初始化扩展
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录以访问此页面。'


# 初始化数据库
db.init_app(app)

# 注册删除功能蓝图
app.register_blueprint(delete_bp, url_prefix='/delete')

# 注册密码管理路由蓝图
app.register_blueprint(password_bp, url_prefix='/password')

# 注册新闻路由蓝图
app.register_blueprint(news_bp, url_prefix='/news')

# 初始化数据库可视化管理后台
admin = init_admin(app, db)

# 初始化定时任务（新闻自动抓取）
init_scheduler()


# 创建上传目录
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(os.path.join(UPLOAD_FOLDER, 'avatars')):
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'avatars'))

if not os.path.exists(os.path.join(UPLOAD_FOLDER, 'posts')):
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'posts'))

if not os.path.exists(os.path.join(UPLOAD_FOLDER, 'videos')):
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'videos'))

if not os.path.exists(os.path.join(UPLOAD_FOLDER, 'attachments')):
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'attachments'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def check_user_permissions():
    """检查用户权限和功能封禁状态"""
    if current_user.is_authenticated:
        # 检查是否完全封禁
        if current_user.is_banned:
            from flask_login import logout_user
            logout_user()
            flash('您的账户已被封禁，请联系管理员解封。', 'danger')
            return redirect(url_for('login'))

        # 检查具体功能封禁并提示
        request_path = request.path

        # 检查发帖权限
        if not current_user.can_post and request_path in ['/create_post', '/edit_post']:
            flash('您的发帖功能已被封禁，请联系管理员解封。', 'danger')
            return redirect(url_for('index'))

        # 检查发视频权限
        if not current_user.can_video and request_path in ['/upload_video', '/edit_video']:
            flash('您的视频上传功能已被封禁，请联系管理员解封。', 'danger')
            return redirect(url_for('index'))

        # 检查评论权限
        if not current_user.can_comment and 'add_comment' in request_path:
            flash('您的评论功能已被封禁，请联系管理员解封。', 'danger')
            return redirect(request.referrer or url_for('index'))


@app.template_global()
def time_ago(dt):
    """计算时间差，返回多久前的描述"""
    from chinese_time_utils import time_ago as util_time_ago
    return util_time_ago(dt)


@app.template_filter('format_chinese_time')
def format_chinese_time(dt):
    """格式化日期时间为中文显示格式（中国标准时间）"""
    from chinese_time_utils import format_datetime_china
    return format_datetime_china(dt)


@app.template_filter('local_time')
def local_time_filter(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """将UTC时间转换为本地时间并在模板中显示"""
    if dt is None:
        return "未知时间"
    return format_datetime_local(dt, format_str)


@app.template_filter('friendly_time')
def friendly_time_filter(dt):
    """将UTC时间转换为友好的中文时间格式"""
    if dt is None:
        return "未知时间"
    return format_datetime_china_friendly(dt)


@app.template_global()
def get_avatar_url(avatar_filename):
    """获取头像URL，处理默认头像逻辑"""
    if not avatar_filename:
        # 如果为空，使用默认头像路径
        return "/static/uploads/avatars/default_avatar.png"

    # 移除可能的重复路径前缀
    avatar_filename = avatar_filename.replace('/static/uploads/avatars/', '').replace(
        'static/uploads/avatars/', '').replace('uploads/avatars/', '')

    # 确保返回正确的路径格式
    return f"/static/uploads/avatars/{avatar_filename}"


@app.template_global()
def get_hot_news(limit=5):
    """获取热门新闻，按点赞数和浏览量排序"""
    from sqlalchemy import func
    # 获取按点赞数和浏览量综合排序的新闻
    hot_news = News.query.order_by(
        (News.likes_count * 2 + News.views * 0.1).desc()  # 点赞权重更高
    ).limit(limit).all()
    return hot_news


@app.template_global()
def is_user_liked_post(post_id):
    """检查当前用户是否点赞了指定帖子"""
    if not current_user.is_authenticated:
        return False
    from models import PostLike
    like = PostLike.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()
    return like is not None


@app.template_global()
def is_user_liked_video(video_id):
    """检查当前用户是否点赞了指定视频"""
    if not current_user.is_authenticated:
        return False
    from models import VideoLike
    like = VideoLike.query.filter_by(
        user_id=current_user.id, video_id=video_id).first()
    return like is not None


@app.template_global()
def is_user_liked_news(news_id):
    """检查当前用户是否点赞了指定新闻"""
    if not current_user.is_authenticated:
        return False
    from models import NewsLike
    like = NewsLike.query.filter_by(
        user_id=current_user.id, news_id=news_id).first()
    return like is not None


@app.template_filter('urlize_with_style')
def urlize_with_style_filter(text):
    """将文本中的URL转换为美化的可点击链接"""
    import re
    url_pattern = re.compile(
        r'(https?://[^\s<>"\)]+)',
        re.IGNORECASE
    )

    def replace_url(match):
        url = match.group(1)
        # 截取显示文本
        display = url
        if len(display) > 50:
            display = display[:47] + '...'
        return (f'<a href="{url}" target="_blank" rel="noopener" '
                f'style="display:inline-flex;align-items:center;gap:6px;'
                f'padding:8px 14px;margin:6px 0;'
                f'background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
                f'color:#fff;text-decoration:none;'
                f'border-radius:8px;font-size:0.9em;font-weight:500;'
                f'box-shadow:0 2px 8px rgba(102,126,234,0.3);'
                f'transition:all 0.3s ease;" '
                f'onmouseover="this.style.transform=\'translateY(-2px)\';this.style.boxShadow=\'0 4px 12px rgba(102,126,234,0.4)\'" '
                f'onmouseout="this.style.transform=\'translateY(0)\';this.style.boxShadow=\'0 2px 8px rgba(102,126,234,0.3)\'"'
                f'>'
                f'<i class="fas fa-external-link-alt" style="font-size:0.85em;"></i>'
                f'<span>查看原文</span>'
                f'</a>')
    result = url_pattern.sub(replace_url, text)
    # 移除"查看详情："文本，只保留链接
    result = result.replace('查看详情：<br>', '')
    result = result.replace('查看详情：', '')
    return result


@app.template_global()
def get_latest_message_between(user1_id, user2_id):
    """获取两个用户之间的最新消息"""
    from models import Message
    # 查询两个用户之间的最新消息
    latest_message = Message.query.filter(
        ((Message.sender_id == user1_id) & (Message.recipient_id == user2_id)) |
        ((Message.sender_id == user2_id) & (Message.recipient_id == user1_id))
    ).order_by(Message.timestamp.desc()).first()
    return latest_message if latest_message else None


@app.template_global()
def get_attachment_url(attachment_path):
    """获取附件URL"""
    if not attachment_path:
        return None

    # 如果已经是完整URL，直接返回
    if attachment_path.startswith(('http://', 'https://')):
        return attachment_path

    # 如果以/static开头，直接返回
    if attachment_path.startswith('/static/'):
        return attachment_path

    # 如果以uploads开头，加上/static前缀
    if attachment_path.startswith('uploads/'):
        return f"/static/{attachment_path}"

    # 否则添加完整的uploads路径
    return f"/static/uploads/{attachment_path}"


@app.template_global()
def attachment_exists(attachment_path):
    """检查附件文件是否存在"""
    import os
    if not attachment_path:
        return False

    # 构建完整的文件路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, 'static', attachment_path)

    # 检查文件是否存在
    return os.path.exists(full_path)


# 创建数据库表
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    # 检查并自动抓取今日新闻
    check_and_fetch_today_news()

    posts = Post.query.order_by(Post.timestamp.desc()).limit(10).all()
    videos = Video.query.order_by(Video.timestamp.desc()).limit(6).all()
    news_items = News.query.order_by(News.timestamp.desc()).limit(5).all()

    # 获取推荐用户（非当前用户关注的用户）
    suggested_users = []
    online_friends = []
    offline_friends = []

    # 为已登录用户创建发布表单
    form = PostForm() if current_user.is_authenticated else None

    if current_user.is_authenticated:
        # 获取当前用户已关注的用户ID
        following_ids = [f.id for f in current_user.followed]
        # 获取不在关注列表中的用户
        suggested_users = User.query.filter(~User.id.in_(following_ids)).filter(
            User.id != current_user.id).limit(10).all()

        # 获取在线和离线好友
        from sqlalchemy import and_
        # 获取当前用户关注的好友
        followed_users = current_user.followed.all()

        # 清理过期的用户状态
        cleanup_expired_user_statuses()

        for user in followed_users:
            # 获取用户状态
            user_status = UserStatus.query.filter_by(user_id=user.id).first()
            if user_status and user_status.is_online:
                online_friends.append({
                    'user': user,
                    'last_seen': user_status.last_online_time
                })
            else:
                # 如果没有状态记录或离线，查找最后活动时间
                last_seen = user.last_seen or user.join_date
                offline_friends.append({
                    'user': user,
                    'last_seen': last_seen
                })
    else:
        suggested_users = User.query.limit(10).all()

    # 获取今日热度排行
    from chinese_time_utils import calculate_daily_trends
    daily_trends = calculate_daily_trends()

    # 获取统计数据
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_videos = Video.query.count()
    total_news = News.query.count()
    total_comments = Comment.query.count()

    # 获取热门新闻（按浏览量）
    hot_news = News.query.order_by(News.views.desc()).limit(5).all()

    # 获取活跃用户（发帖最多的用户）
    from sqlalchemy import func
    active_users = db.session.query(
        User, func.count(Post.id).label('post_count')
    ).join(Post, User.id == Post.author_id
           ).group_by(User.id
                      ).order_by(func.count(Post.id).desc()
                                 ).limit(5).all()

    return render_template('index.html',
                           posts=posts,
                           videos=videos,
                           news_items=news_items,
                           suggested_users=suggested_users,
                           online_friends=online_friends,
                           offline_friends=offline_friends,
                           daily_trends=daily_trends,
                           form=form,
                           total_users=total_users,
                           total_posts=total_posts,
                           total_videos=total_videos,
                           total_news=total_news,
                           total_comments=total_comments,
                           hot_news=hot_news,
                           active_users=active_users)


def cleanup_expired_user_statuses():
    """清理长时间未活动的用户状态 - 定期任务"""
    with app.app_context():
        # 将超过2分钟没有更新状态的用户标记为离线
        two_minutes_ago = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - timedelta(minutes=2)

        # 查找所有最后活动时间超过2分钟的在线用户
        expired_statuses = UserStatus.query.filter(
            UserStatus.is_online == True,
            UserStatus.last_online_time < two_minutes_ago
        ).all()

        updated_count = 0
        for status in expired_statuses:
            was_online = status.is_online
            status.is_online = False
            status.last_offline_time = get_current_time().astimezone(
                timezone.utc).replace(tzinfo=None)

            # 如果用户之前是在线状态，通知其好友
            if was_online:
                user = User.query.get(status.user_id)
                if user:
                    status_change_data = {
                        'user_id': status.user_id,
                        'username': user.username,
                        'is_online': False,
                        'last_seen': time_ago(status.last_offline_time) if status.last_offline_time else '未知时间'
                    }

                    # 通知所有关注该用户的好友
                    notify_friends_about_status_change(
                        status.user_id, status_change_data)

            updated_count += 1

        if updated_count > 0:
            db.session.commit()


# 定期清理过期用户状态
def start_status_cleanup_timer():
    """启动定期清理过期用户状态的定时器"""
    def timer_loop():
        try:
            cleanup_expired_user_statuses()
            time.sleep(60)  # 每1分钟清理一次
        except Exception as e:
            print(f"清理用户状态时出错: {e}")
            time.sleep(60)  # 出错后继续等待1分钟再试

    # 启动清理线程
    cleanup_thread = threading.Thread(target=timer_loop, daemon=True)
    cleanup_thread.start()


# 启动状态清理定时器
start_status_cleanup_timer()


@app.route('/post_detail/<int:post_id>')
def post_detail(post_id):
    """帖子详情页面"""
    post = Post.query.get_or_404(post_id)

    # 获取评论并按时间排序
    comments = Comment.query.filter_by(
        post_id=post_id).order_by(Comment.timestamp.asc()).all()

    # 创建评论表单
    form = CommentForm()

    # 获取相关帖子（同作者的其他帖子，最多5个）
    related_posts = Post.query.filter(
        Post.author_id == post.author_id,
        Post.id != post_id  # 排除当前帖子
    ).order_by(Post.timestamp.desc()).limit(5).all()

    return render_template('post_detail.html',
                           post=post,
                           comments=comments,
                           form=form,
                           related_posts=related_posts)


@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    """添加评论"""
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            author=current_user,
            post_id=post_id
        )
        db.session.add(comment)
        # 更新帖子评论计数
        post.comments_count = Comment.query.filter_by(post_id=post_id).count()
        db.session.commit()
        flash('评论已发布', 'success')
    else:
        for error in form.errors.values():
            flash(','.join(error), 'danger')

    return redirect(url_for('post_detail', post_id=post_id))


def check_and_fetch_today_news():
    """检查今天是否有新闻，没有则自动抓取"""
    from datetime import date
    today = date.today()

    # 检查今天是否已有新闻
    today_news_count = News.query.filter(
        db.func.date(News.timestamp) == today
    ).count()

    if today_news_count == 0:
        # 今天没有新闻，触发抓取（在后台线程中执行，避免阻塞请求）
        def fetch_in_background():
            try:
                with app.app_context():
                    from news_scraper_v2 import NewsScraper, save_scraper_news
                    print(f"[{datetime.now()}] 检测到今日无新闻，开始自动抓取...")
                    scraper = NewsScraper()
                    news_list = scraper.scrape_all()
                    if news_list:
                        saved = save_scraper_news(news_list)
                        print(f"[{datetime.now()}] 自动抓取完成，保存 {saved} 条新闻")
                    else:
                        print(f"[{datetime.now()}] 自动抓取未获取到新闻")
            except Exception as e:
                print(f"[{datetime.now()}] 自动抓取新闻失败: {e}")

        # 使用标记避免重复触发
        cache_key = f'news_fetching_{today}'
        if not getattr(app, '_news_fetching', False):
            app._news_fetching = True
            t = threading.Thread(target=fetch_in_background, daemon=True)
            t.start()
            # 5分钟后重置标记，允许再次检查

            def reset_flag():
                import time as _time
                _time.sleep(300)
                app._news_fetching = False
            threading.Thread(target=reset_flag, daemon=True).start()

        return False  # 今天暂无新闻
    return True  # 今天有新闻


@app.route('/news')
def news():
    """新闻页面"""
    # 检查并自动抓取今日新闻
    check_and_fetch_today_news()

    # 获取页码参数
    page = request.args.get('page', 1, type=int)
    # 每页显示 10 条新闻
    per_page = 10

    # 分页查询新闻，按时间倒序排列
    pagination = News.query.order_by(News.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    news_items = pagination.items

    return render_template('news.html', news_items=news_items, pagination=pagination)


@app.context_processor
def inject_news_utils():
    """为模板注入新闻相关的工具函数"""
    def get_last_news_update():
        """获取最新新闻的更新时间"""
        latest_news = News.query.order_by(News.timestamp.desc()).first()
        if latest_news:
            return latest_news.timestamp.strftime('%Y-%m-%d %H:%M')
        return None

    return dict(get_last_news_update=get_last_news_update)


@app.route('/videos')
def videos():
    """视频页面"""
    # 获取最新的视频，按时间倒序排列
    videos = Video.query.order_by(Video.timestamp.desc()).all()
    return render_template('videos.html', videos=videos)


@app.route('/trending')
def trending():
    """热度排行页面"""
    from utils import calculate_daily_trends
    trending_items = calculate_daily_trends()
    return render_template('trending.html',
                           trending_items=trending_items,
                           period='每日')


@app.route('/forum')
def forum():
    """论坛页面"""
    # 获取最新的帖子，按时间倒序排列
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    # 创建发布帖子的表单
    form = PostForm() if current_user.is_authenticated else None

    # 获取今日热度排行（用于右侧边栏显示）
    from chinese_time_utils import calculate_daily_trends
    daily_trends = calculate_daily_trends()

    return render_template('forum.html', posts=posts, form=form, daily_trends=daily_trends)


@app.route('/search')
def search():
    """搜索功能"""
    query = request.args.get('q', '')
    if query:
        # 搜索用户
        users = User.query.filter(User.username.contains(query)).all()
        # 搜索帖子
        posts = Post.query.filter(Post.title.contains(
            query) | Post.content.contains(query)).all()
        # 搜索视频
        videos = Video.query.filter(Video.title.contains(
            query) | Video.description.contains(query)).all()

        # 组合搜索结果
        results = []
        for user in users:
            results.append({'type': 'user', 'data': user,
                           'display_name': user.username})
        for post in posts:
            results.append({'type': 'post', 'data': post,
                           'display_name': post.title})
        for video in videos:
            results.append({'type': 'video', 'data': video,
                           'display_name': video.title})
    else:
        results = []

    return render_template('search_results.html', results=results, query=query)


@app.route('/calendar')
def calendar():
    """日历页面 - 显示重要日期和事件"""
    # 这里可以实现日历功能，目前返回一个简单的日历页面
    from datetime import datetime
    current_date = datetime.now()

    # 可以在这里添加事件和活动信息
    events = []

    return render_template('calendar.html',
                           current_date=current_date,
                           events=events)


@app.route('/about')
def about():
    """关于我们页面"""
    return render_template('about.html')


@app.route('/profile/<username>')
def profile(username):
    """用户个人资料页面"""
    user = User.query.filter_by(username=username).first_or_404()

    # 获取用户发布的帖子
    user_posts = Post.query.filter_by(
        author_id=user.id).order_by(Post.timestamp.desc()).all()

    # 获取用户上传的视频
    user_videos = Video.query.filter_by(
        uploader_id=user.id).order_by(Video.timestamp.desc()).all()

    # 检查当前用户是否关注了该用户
    is_following = False
    if current_user.is_authenticated:
        is_following = current_user.is_following(user)

    return render_template('profile.html',
                           user=user,
                           posts=user_posts,
                           videos=user_videos,
                           is_following=is_following)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """编辑个人资料页面"""
    form = ProfileForm(
        current_username=current_user.username, obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data

        # 处理头像上传
        if form.avatar.data and hasattr(form.avatar.data, 'filename') and form.avatar.data.filename:
            avatar_file = form.avatar.data
            avatar_filename = save_image(avatar_file, os.path.join(
                UPLOAD_FOLDER, 'avatars'), size=(150, 150))
            current_user.avatar = avatar_filename

        db.session.commit()
        flash('个人资料已更新', 'success')
        return redirect(url_for('profile', username=current_user.username))

    return render_template('edit_profile.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        # 验证验证码
        if 'captcha' in session:
            entered_captcha = form.captcha.data
            stored_captcha = session.get('captcha', '')

            if entered_captcha.upper() != stored_captcha.upper():
                flash('验证码错误', 'danger')
                return render_template('auth/login.html', form=form)
        else:
            flash('验证码已失效，请刷新页面重试', 'danger')
            return render_template('auth/login.html', form=form)

        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # 检查用户是否被封禁
            if user.is_banned:
                flash('您的账户已被封禁，无法登录。请联系管理员了解详情。', 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        flash('用户名或密码错误', 'danger')

    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # 验证验证码
        if 'captcha' in session:
            entered_captcha = form.captcha.data
            stored_captcha = session.get('captcha', '')

            if entered_captcha.upper() != stored_captcha.upper():
                flash('验证码错误', 'danger')
                return render_template('auth/register.html', form=form)
        else:
            flash('验证码已失效，请刷新页面重试', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功，请登录', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """用户登出"""
    logout_user()
    return redirect(url_for('index'))


@app.route('/messages')
@login_required
def messages():
    """消息中心页面"""
    # 获取收到的消息 - 使用Query而不是直接访问关系属性
    received_messages = Message.query.filter_by(
        recipient_id=current_user.id).order_by(
        Message.timestamp.desc()).all()
    # 获取发送的消息 - 使用Query而不是直接访问关系属性
    sent_messages = Message.query.filter_by(
        sender_id=current_user.id).order_by(
        Message.timestamp.desc()).all()

    # 合并并按时间排序
    all_messages = sorted(received_messages + sent_messages,
                          key=lambda x: x.timestamp, reverse=True)

    # 获取最近联系人
    recent_contacts = []
    processed_usernames = set()
    for msg in all_messages:
        partner = msg.sender if msg.recipient_id == current_user.id else msg.recipient
        if partner.username not in processed_usernames:
            recent_contacts.append(partner)
            processed_usernames.add(partner.username)
            if len(recent_contacts) >= 10:  # 限制为最近10个联系人
                break

    return render_template('messages.html',
                           all_messages=all_messages,
                           recent_contacts=recent_contacts)


@app.route('/chat/<recipient>')
@login_required
def chat_window(recipient):
    """聊天窗口页面"""
    recipient_user = User.query.filter_by(username=recipient).first_or_404()

    # 获取与该用户的聊天记录
    chat_messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_user.id)) |
        ((Message.sender_id == recipient_user.id) &
         (Message.recipient_id == current_user.id))
    ).order_by(Message.timestamp.asc()).all()

    # 为每条消息添加附件URL和关系信息
    for message in chat_messages:
        if message.attachment_path:
            # 使用与模板函数相同的逻辑构造URL
            if message.attachment_path.startswith(('http://', 'https://')):
                message.attachment_url = message.attachment_path
            elif message.attachment_path.startswith('/static/'):
                message.attachment_url = message.attachment_path
            elif message.attachment_path.startswith('uploads/'):
                message.attachment_url = f"/static/{message.attachment_path}"
            else:
                message.attachment_url = f"/static/uploads/{message.attachment_path}"
        else:
            message.attachment_url = None

        # 设置消息发送者与当前用户的关系
        if message.sender_id != current_user.id:
            # 检查是否是好友（互相关注）
            if current_user.is_following(message.sender) and message.sender.is_following(current_user):
                message.is_friend = True
                message.is_followed = False
            elif current_user.is_following(message.sender):
                message.is_friend = False
                message.is_followed = True
            else:
                message.is_friend = False
                message.is_followed = False
        else:
            message.is_friend = False
            message.is_followed = False

    # 计算与该用户的消息统计
    sent_to_recipient = Message.query.filter_by(
        sender_id=current_user.id,
        recipient_id=recipient_user.id
    ).count()

    received_from_recipient = Message.query.filter_by(
        sender_id=recipient_user.id,
        recipient_id=current_user.id
    ).count()

    form = MessageForm()
    return render_template('chat_window.html',
                           recipient=recipient_user,
                           chat_messages=chat_messages,
                           sent_to_recipient=sent_to_recipient,
                           received_from_recipient=received_from_recipient,
                           form=form)


@app.route('/send_message/<recipient_username>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_username):
    """发送消息给指定用户"""
    recipient = User.query.filter_by(
        username=recipient_username).first_or_404()
    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            sender=current_user,
            recipient=recipient,
            content=form.content.data
        )

        # 处理附件上传
        if form.attachment.data:
            attachment_file = form.attachment.data
            filename = secure_filename(attachment_file.filename)
            if filename:
                # 生成唯一文件名
                unique_filename = generate_filename(filename)
                filepath = os.path.join(
                    UPLOAD_FOLDER, 'attachments', unique_filename)

                # 确保目录存在
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                attachment_file.save(filepath)

                # 根据文件扩展名设置附件类型
                file_ext = unique_filename.lower().split(
                    '.')[-1] if '.' in unique_filename else ''
                if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                    message.attachment_type = 'image'
                elif file_ext in ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm', 'flv', 'm4v']:
                    message.attachment_type = 'video'
                elif file_ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']:
                    message.attachment_type = 'audio'
                else:
                    message.attachment_type = 'file'

                message.attachment_path = f'uploads/attachments/{unique_filename}'
                message.attachment_filename = filename

        db.session.add(message)
        db.session.commit()

        flash('消息已发送', 'success')
        return redirect(url_for('chat_window', recipient=recipient_username))

    return render_template('send_message.html',
                           form=form,
                           recipient=recipient)


@app.route('/admin')
@login_required
def admin():
    """管理员面板 - 总览页"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('index'))

    users = User.query.all()
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    all_videos = Video.query.order_by(Video.timestamp.desc()).all()
    all_news = News.query.order_by(News.timestamp.desc()).all()
    all_comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    ban_form = AdminUserBanForm()

    return render_template('admin_dashboard/index.html',
                           users=users,
                           posts=posts,
                           videos=all_videos,
                           news_list=all_news,
                           comments=all_comments,
                           ban_form=ban_form)


@app.route('/admin/users')
@login_required
def admin_users():
    """管理员 - 用户管理"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    ban_form = AdminUserBanForm()
    return render_template('admin_dashboard/users.html', users=users, ban_form=ban_form)


@app.route('/admin/content')
@login_required
def admin_content():
    """管理员 - 内容管理"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    all_videos = Video.query.order_by(Video.timestamp.desc()).all()
    all_news = News.query.order_by(News.timestamp.desc()).all()
    all_comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return render_template('admin_dashboard/content.html',
                           posts=posts, videos=all_videos,
                           news_list=all_news, comments=all_comments)


@app.route('/admin/test')
@login_required
def admin_test():
    """管理员 - 测试面板"""
    if not current_user.is_admin:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('index'))
    return render_template('admin_dashboard/test.html')


@app.route('/admin/ban_user/<int:user_id>', methods=['POST'])
@login_required
def ban_user(user_id):
    """封禁用户"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    user = User.query.get_or_404(user_id)
    ban_type = request.form.get('ban_type', 'full')
    reason = request.form.get('reason', '')
    if ban_type == 'full':
        user.is_banned = True
        user.is_active = False
    elif ban_type == 'post':
        user.can_post = False
    elif ban_type == 'video':
        user.can_video = False
    elif ban_type == 'comment':
        user.can_comment = False
    db.session.commit()
    flash(f'用户 {user.username} 已被封禁（类型：{ban_type}），原因：{reason}', 'warning')
    return redirect(url_for('admin_users'))


@app.route('/admin/unban_user/<int:user_id>')
@login_required
def unban_user(user_id):
    """解封用户"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    user.is_active = True
    user.can_post = True
    user.can_video = True
    user.can_comment = True
    db.session.commit()
    flash(f'用户 {user.username} 已解封', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/ban_post_only/<int:user_id>')
@login_required
def ban_post_only(user_id):
    """禁止发帖"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_post = False
    db.session.commit()
    flash(f'✅ 已禁止用户 {user.username} 发帖', 'warning')
    return redirect(url_for('admin_users'))


@app.route('/admin/ban_video_only/<int:user_id>')
@login_required
def ban_video_only(user_id):
    """禁止发视频"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_video = False
    db.session.commit()
    flash(f'✅ 已禁止用户 {user.username} 发视频', 'warning')
    return redirect(url_for('admin_users'))


@app.route('/admin/ban_comment_only/<int:user_id>')
@login_required
def ban_comment_only(user_id):
    """禁止评论"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_comment = False
    db.session.commit()
    flash(f'✅ 已禁止用户 {user.username} 评论', 'warning')
    return redirect(url_for('admin_users'))


@app.route('/admin/unban_post_only/<int:user_id>')
@login_required
def unban_post_only(user_id):
    """允许发帖"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_post = True
    db.session.commit()
    flash(f'✅ 已允许用户 {user.username} 发帖', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/unban_video_only/<int:user_id>')
@login_required
def unban_video_only(user_id):
    """允许发视频"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_video = True
    db.session.commit()
    flash(f'✅ 已允许用户 {user.username} 发视频', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/unban_comment_only/<int:user_id>')
@login_required
def unban_comment_only(user_id):
    """允许评论"""
    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))
    user = User.query.get_or_404(user_id)
    user.can_comment = True
    db.session.commit()
    flash(f'✅ 已允许用户 {user.username} 评论', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/reset_password/<int:user_id>')
@login_required
def admin_reset_password(user_id):
    """管理员重置用户密码"""
    from werkzeug.security import generate_password_hash
    import random
    from flask import session

    if not current_user.is_admin:
        flash('无权操作', 'danger')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)

    # 生成8位随机密码（字母+数字）
    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    new_password = ''.join([random.choice(chars) for _ in range(8)])
    user.password_hash = generate_password_hash(new_password)

    # 记录日志
    from models import PasswordChangeLog
    log = PasswordChangeLog(
        user_id=user.id,
        changed_by='admin',
        ip_address=request.remote_addr,
        reason=f'管理员 {current_user.username} 重置密码'
    )
    db.session.add(log)
    db.session.commit()

    # 使用session临时存储密码
    session['last_reset_password'] = {
        'username': user.username,
        'password': new_password
    }

    flash(
        f'✅ 已重置用户 {user.username} 的密码为: {new_password}，请立即通知用户！此密码只显示一次', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/toggle_admin/<int:user_id>')
@login_required
def toggle_admin(user_id):
    """切换用户管理员权限"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('不能修改自己的管理员权限', 'danger')
        return redirect(url_for('admin_users'))
    user.is_admin = not user.is_admin
    db.session.commit()
    status = '管理员' if user.is_admin else '普通用户'
    flash(f'用户 {user.username} 已设置为{status}', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@login_required
def admin_delete_post(post_id):
    """管理员删除帖子"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    post = Post.query.get_or_404(post_id)
    PostLike.query.filter_by(post_id=post_id).delete()
    Comment.query.filter_by(post_id=post_id).delete()
    db.session.delete(post)
    db.session.commit()
    flash(f'帖子 "{post.title}" 已删除', 'success')
    return redirect(url_for('admin_content'))


@app.route('/admin/delete_news/<int:news_id>', methods=['POST'])
@login_required
def admin_delete_news(news_id):
    """管理员删除新闻"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    news_item = News.query.get_or_404(news_id)
    NewsLike.query.filter_by(news_id=news_id).delete()
    Comment.query.filter_by(news_id=news_id).delete()
    NewsOperationLog.query.filter_by(news_id=news_id).delete()
    db.session.delete(news_item)
    db.session.commit()
    flash(f'新闻 "{news_item.title}" 已删除', 'success')
    return redirect(url_for('admin_content'))


@app.route('/admin/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def admin_delete_comment(comment_id):
    """管理员删除评论"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    comment = Comment.query.get_or_404(comment_id)
    # 更新关联内容的评论数
    if comment.post_id:
        post = Post.query.get(comment.post_id)
        if post:
            post.comments_count = max(0, (post.comments_count or 0) - 1)
    if comment.news_id:
        news_item = News.query.get(comment.news_id)
        if news_item:
            news_item.comments_count = max(
                0, (news_item.comments_count or 0) - 1)
    if comment.video_id:
        video = Video.query.get(comment.video_id)
        if video:
            video.comments_count = max(0, (video.comments_count or 0) - 1)
    db.session.delete(comment)
    db.session.commit()
    flash('评论已删除', 'success')
    return redirect(url_for('admin_content'))


@app.route('/admin/api/test_db')
@login_required
def admin_test_db():
    """测试数据库连接"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    try:
        user_count = User.query.count()
        post_count = Post.query.count()
        news_count = News.query.count()
        video_count = Video.query.count()
        comment_count = Comment.query.count()
        return jsonify({
            'success': True,
            'message': '数据库连接正常',
            'stats': {
                'users': user_count,
                'posts': post_count,
                'news': news_count,
                'videos': video_count,
                'comments': comment_count
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'数据库错误: {str(e)}'})


@app.route('/admin/api/test_news_scraper')
@login_required
def admin_test_news_scraper():
    """测试新闻抓取器"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    try:
        from news_scraper_v2 import NewsScraper
        scraper = NewsScraper()
        # 只测试一个源
        news_list = scraper.fetch_xinhua_news()
        return jsonify({
            'success': True,
            'message': f'新闻抓取器正常，获取到 {len(news_list)} 条新华网新闻',
            'sample': news_list[0] if news_list else None
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'新闻抓取器错误: {str(e)}'})


@app.route('/admin/api/test_routes')
@login_required
def admin_test_routes():
    """测试所有路由是否正常"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    results = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            results.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
                'url': rule.rule
            })
    return jsonify({'success': True, 'routes': results, 'total': len(results)})


@app.route('/admin/api/fetch_news_now', methods=['POST'])
@login_required
def admin_fetch_news_now():
    """手动触发新闻抓取"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    try:
        from news_scraper_v2 import NewsScraper, save_scraper_news
        scraper = NewsScraper()
        news_list = scraper.scrape_all()
        if news_list:
            saved = save_scraper_news(news_list)
            return jsonify({'success': True, 'message': f'抓取完成，保存了 {saved} 条新闻'})
        else:
            return jsonify({'success': True, 'message': '未获取到新闻'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'抓取失败: {str(e)}'})


@app.route('/admin/api/system_info')
@login_required
def admin_system_info():
    """获取系统信息"""
    if not current_user.is_admin:
        return jsonify({'error': '无权操作'}), 403
    import sys
    import platform
    db_path = app.config.get('SQLALCHEMY_DATABASE_URI', 'unknown')
    return jsonify({
        'success': True,
        'info': {
            'python_version': sys.version,
            'platform': platform.platform(),
            'flask_debug': app.debug,
            'database': db_path,
            'secret_key_set': bool(app.config.get('SECRET_KEY')),
        }
    })


@app.route('/follow/<username>')
@login_required
def follow(username):
    """关注用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在', 'error')
        return redirect(url_for('index'))

    if user == current_user:
        flash('您不能关注自己', 'error')
        return redirect(url_for('profile', username=username))

    current_user.follow(user)
    db.session.commit()
    flash(f'您现在已关注 {username}', 'success')

    return redirect(url_for('profile', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """取消关注用户"""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户不存在', 'error')
        return redirect(url_for('index'))

    if user == current_user:
        flash('您不能取消关注自己', 'error')
        return redirect(url_for('profile', username=username))

    current_user.unfollow(user)
    db.session.commit()
    flash(f'您已取消关注 {username}', 'success')

    return redirect(url_for('profile', username=username))


@app.route('/user/<username>/following')
def show_following(username):
    """显示用户关注列表"""
    user = User.query.filter_by(username=username).first_or_404()
    following = user.followed.all()
    return render_template('user_list.html', users=following, title=f'{username} 关注的人')


@app.route('/user/<username>/followers')
def show_followers(username):
    """显示用户粉丝列表"""
    user = User.query.filter_by(username=username).first_or_404()
    followers = user.followers.all()
    return render_template('user_list.html', users=followers, title=f'{username} 的粉丝')


@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    """点赞帖子"""
    post = Post.query.get_or_404(post_id)

    # 检查用户是否已点赞
    existing_like = PostLike.query.filter_by(
        user_id=current_user.id, post_id=post_id).first()

    if existing_like:
        # 如果已点赞，则取消点赞
        db.session.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)  # 确保不会变成负数
        liked = False
    else:
        # 如果未点赞，则添加点赞
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post.likes_count += 1
        liked = True

    db.session.commit()

    return jsonify({'liked': liked, 'likes_count': post.likes_count})


@app.route('/like_video/<int:video_id>', methods=['POST'])
@login_required
def like_video(video_id):
    """点赞视频"""
    video = Video.query.get_or_404(video_id)

    # 检查用户是否已点赞
    existing_like = VideoLike.query.filter_by(
        user_id=current_user.id, video_id=video_id).first()

    if existing_like:
        # 如果已点赞，则取消点赞
        db.session.delete(existing_like)
        video.likes_count = max(0, video.likes_count - 1)  # 确保不会变成负数
        liked = False
    else:
        # 如果未点赞，则添加点赞
        like = VideoLike(user_id=current_user.id, video_id=video_id)
        db.session.add(like)
        video.likes_count += 1
        liked = True

    db.session.commit()

    return jsonify({'liked': liked, 'likes_count': video.likes_count})


@app.route('/like_news/<int:news_id>', methods=['POST'])
@login_required
def like_news(news_id):
    """点赞新闻"""
    news = News.query.get_or_404(news_id)

    # 检查用户是否已点赞
    existing_like = NewsLike.query.filter_by(
        user_id=current_user.id, news_id=news_id).first()

    old_likes_count = news.likes_count or 0

    if existing_like:
        # 如果已点赞，则取消点赞
        db.session.delete(existing_like)
        news.likes_count = max(0, news.likes_count - 1)  # 确保不会变成负数
        liked = False
        operation_type = 'unlike'
    else:
        # 如果未点赞，则添加点赞
        like = NewsLike(user_id=current_user.id, news_id=news_id)
        db.session.add(like)
        news.likes_count += 1
        liked = True
        operation_type = 'like'

    db.session.commit()

    # 记录点赞操作日志
    from flask import request
    log = NewsOperationLog(
        news_id=news.id,
        user_id=current_user.id,
        operation_type=operation_type,
        old_value=old_likes_count,
        new_value=news.likes_count,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'liked': liked, 'likes_count': news.likes_count})


@app.route('/like_<type>/<int:id>', methods=['POST'])
@login_required
def like_generic(type, id):
    """通用点赞接口，处理前端的动态请求"""
    if type == 'post':
        return like_post(id)
    elif type == 'video':
        return like_video(id)
    elif type == 'news':
        return like_news(id)
    else:
        return jsonify({'error': '不支持的类型'}), 400


@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    """编辑帖子"""
    post = Post.query.get_or_404(post_id)

    # 检查用户权限（必须是帖子作者或管理员）
    if post.author != current_user and not current_user.is_admin:
        flash('您没有权限编辑此帖子', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        # 处理图片上传
        if form.image.data:
            image_file = form.image.data
            image_filename = save_image(image_file, os.path.join(
                UPLOAD_FOLDER, 'posts'), size=(800, 600))
            post.image_url = f'uploads/posts/{image_filename}'

        # 处理视频上传
        if form.video.data:
            video_file = form.video.data
            video_filename = save_file(
                video_file, os.path.join(UPLOAD_FOLDER, 'posts'))
            post.video_url = f'uploads/posts/{video_filename}'

        db.session.commit()
        flash('帖子已更新', 'success')
        return redirect(url_for('post_detail', post_id=post.id))

    return render_template('edit_post.html', form=form, post=post)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    """创建新帖子"""
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )

        # 处理图片上传
        if form.image.data:
            image_file = form.image.data
            image_filename = save_image(image_file, os.path.join(
                UPLOAD_FOLDER, 'posts'), size=(800, 600))
            post.image_url = f'uploads/posts/{image_filename}'

        # 处理视频上传
        if form.video.data:
            video_file = form.video.data
            video_filename = save_file(
                video_file, os.path.join(UPLOAD_FOLDER, 'posts'))
            post.video_url = f'uploads/posts/{video_filename}'

        db.session.add(post)
        db.session.commit()
        flash('帖子已发布', 'success')
        return redirect(url_for('index'))

    return render_template('create_post.html', form=form)


@app.route('/upload_video', methods=['GET', 'POST'])
@login_required
def upload_video():
    """上传视频"""
    form = VideoForm()
    if form.validate_on_submit():
        # 处理视频文件上传
        video_file = form.video_file.data
        video_filename = save_file(
            video_file, os.path.join(UPLOAD_FOLDER, 'videos'))
        video_url = f'uploads/videos/{video_filename}'

        # 处理缩略图上传
        thumbnail_filename = None
        if form.thumbnail.data:
            thumbnail_file = form.thumbnail.data
            thumbnail_filename = save_image(thumbnail_file, os.path.join(
                UPLOAD_FOLDER, 'thumbnails'), size=(400, 300))
            thumbnail_url = f'uploads/thumbnails/{thumbnail_filename}'
        else:
            # 如果没有上传缩略图，使用默认缩略图或从视频生成
            thumbnail_url = 'images/default_video_thumbnail.jpg'

        # 创建视频记录
        video = Video(
            title=form.title.data,
            description=form.description.data,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            uploader_id=current_user.id
        )

        db.session.add(video)
        db.session.commit()

        flash('视频上传成功', 'success')
        return redirect(url_for('videos'))

    return render_template('upload_video.html', form=form)


@app.route('/edit_video/<int:video_id>', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    """编辑视频"""
    video = Video.query.get_or_404(video_id)

    # 检查用户权限（必须是视频上传者或管理员）
    if video.uploader != current_user and not current_user.is_admin:
        flash('您没有权限编辑此视频', 'danger')
        return redirect(url_for('video_detail', video_id=video_id))

    form = VideoForm(obj=video)
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data

        # 处理缩略图上传
        if form.thumbnail.data:
            thumbnail_file = form.thumbnail.data
            thumbnail_filename = save_image(thumbnail_file, os.path.join(
                UPLOAD_FOLDER, 'posts'), size=(400, 300))
            video.thumbnail_url = f'uploads/posts/{thumbnail_filename}'

        db.session.commit()
        flash('视频已更新', 'success')
        return redirect(url_for('video_detail', video_id=video.id))

    return render_template('edit_video.html', form=form, video=video)


@app.route('/delete_video/<int:video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    """删除视频"""
    video = Video.query.get_or_404(video_id)

    # 检查用户权限（必须是视频上传者或管理员）
    if video.uploader != current_user and not current_user.is_admin:
        flash('您没有权限删除此视频', 'danger')
        return redirect(url_for('video_detail', video_id=video_id))

    # 创建删除记录
    history = ContentHistory(
        content_type='video',
        content_id=video.id,
        field_name='deleted',
        old_value=video.title,
        new_value='[已删除]',
        user_id=current_user.id
    )
    db.session.add(history)

    # 删除相关的点赞和评论
    VideoLike.query.filter_by(video_id=video_id).delete()
    Comment.query.filter_by(video_id=video_id).delete()

    # 删除视频记录
    db.session.delete(video)
    db.session.commit()

    flash('视频已删除', 'success')
    return redirect(url_for('videos'))


@app.route('/news_detail/<int:news_id>')
def news_detail(news_id):
    """新闻详情页面"""
    news_item = News.query.get_or_404(news_id)

    # 增加浏览量并记录日志
    old_views = news_item.views or 0
    news_item.views = old_views + 1
    db.session.commit()

    # 记录查看操作日志
    from flask import request
    log = NewsOperationLog(
        news_id=news_item.id,
        user_id=current_user.id if current_user.is_authenticated else None,
        operation_type='view',
        old_value=old_views,
        new_value=news_item.views,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(log)
    db.session.commit()

    # 获取相关新闻（同一天发布的新闻，排除当前新闻）
    from sqlalchemy import extract
    related_news = News.query.filter(
        extract('year', News.timestamp) == extract(
            'year', news_item.timestamp),
        extract('month', News.timestamp) == extract(
            'month', news_item.timestamp),
        extract('day', News.timestamp) == extract('day', news_item.timestamp),
        News.id != news_id
    ).order_by(News.timestamp.desc()).limit(5).all()

    # 获取评论
    comments = Comment.query.filter_by(
        news_id=news_id).order_by(Comment.timestamp.asc()).all()

    # 创建评论表单
    form = CommentForm()

    return render_template('news_detail.html',
                           news=news_item,
                           related_news=related_news,
                           comments=comments,
                           comment_form=form)


@app.route('/video_detail/<int:video_id>')
@login_required
def video_detail(video_id):
    """视频详情页面"""
    video = Video.query.get_or_404(video_id)

    # 增加观看次数
    video.views = video.views + 1 if video.views else 1
    db.session.commit()

    # 获取相关视频（同一上传者的其他视频，最多5个）
    related_videos = Video.query.filter(
        Video.uploader_id == video.uploader_id,
        Video.id != video_id  # 排除当前视频
    ).order_by(Video.timestamp.desc()).limit(5).all()

    # 获取评论
    comments = Comment.query.filter_by(
        video_id=video_id).order_by(Comment.timestamp.asc()).all()

    # 创建评论表单
    form = CommentForm()

    return render_template('video_detail.html',
                           video=video,
                           related_videos=related_videos,
                           comments=comments,
                           form=form)


@app.route('/add_news_comment/<int:news_id>', methods=['POST'])
@login_required
def add_news_comment(news_id):
    """添加新闻评论"""
    news = News.query.get_or_404(news_id)
    form = CommentForm()

    if form.validate_on_submit():
        old_comments_count = news.comments_count or 0

        comment = Comment(
            content=form.content.data,
            author=current_user,
            news_id=news_id
        )
        db.session.add(comment)

        # 增加新闻的评论数
        news.comments_count = old_comments_count + 1
        db.session.commit()

        # 记录评论操作日志
        from flask import request
        log = NewsOperationLog(
            news_id=news.id,
            user_id=current_user.id,
            operation_type='comment',
            old_value=old_comments_count,
            new_value=news.comments_count,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log)
        db.session.commit()

        flash('评论已发布', 'success')
    else:
        for error in form.errors.values():
            flash(','.join(error), 'danger')

    return redirect(url_for('news_detail', news_id=news_id))


@app.route('/add_comment_to_video/<int:video_id>', methods=['POST'])
@login_required
def add_comment_to_video(video_id):
    """添加视频评论"""
    video = Video.query.get_or_404(video_id)
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            author=current_user,
            video_id=video_id
        )
        db.session.add(comment)
        # 更新视频的评论计数
        video.comments_count = (video.comments_count or 0) + 1
        db.session.commit()
        flash('评论已发布', 'success')
    else:
        for error in form.errors.values():
            flash(','.join(error), 'danger')

    return redirect(url_for('video_detail', video_id=video_id))


@app.route('/video/<int:video_id>/view', methods=['POST'])
def track_video_view(video_id):
    """记录视频观看次数"""
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()
    return jsonify({'views': video.views})


@app.route('/trending_daily')
def trending_daily():
    """每日热度排行页面"""
    from chinese_time_utils import calculate_daily_trends
    daily_trends = calculate_daily_trends()
    return render_template('trending.html',
                           trending_items=daily_trends,
                           period='daily')


@app.route('/trending_weekly')
def trending_weekly():
    """每周热度排行页面"""
    # 这里可以实现每周热度排行逻辑
    # 临时使用每日热度排行逻辑，实际应根据周计算
    from chinese_time_utils import calculate_daily_trends
    weekly_trends = calculate_daily_trends()
    return render_template('trending.html',
                           trending_items=weekly_trends,
                           period='weekly')


@app.route('/trending_monthly')
def trending_monthly():
    """每月热度排行页面"""
    # 这里可以实现每月热度排行逻辑
    # 临时使用每日热度排行逻辑，实际应根据月计算
    from chinese_time_utils import calculate_daily_trends
    monthly_trends = calculate_daily_trends()
    return render_template('trending.html',
                           trending_items=monthly_trends,
                           period='monthly')


@app.route('/api/update_user_status', methods=['POST'])
@login_required
def api_update_user_status():
    """更新用户状态（用于心跳检测）"""
    from flask import request
    data = request.get_json()

    user_status = UserStatus.query.filter_by(user_id=current_user.id).first()
    was_online = False

    if user_status:
        was_online = user_status.is_online
        user_status.is_online = True
        user_status.last_online_time = get_current_time(
        ).astimezone(timezone.utc).replace(tzinfo=None)
    else:
        user_status = UserStatus(
            user_id=current_user.id, is_online=True, last_online_time=get_current_time().astimezone(timezone.utc).replace(tzinfo=None))
        db.session.add(user_status)

    db.session.commit()

    # 如果用户之前是离线的，通知好友
    if not was_online:
        status_change_data = {
            'user_id': current_user.id,
            'username': current_user.username,
            'is_online': True,
            'last_seen': time_ago(get_current_time().astimezone(timezone.utc).replace(tzinfo=None))
        }
        notify_friends_about_status_change(current_user.id, status_change_data)

    return jsonify({'success': True, 'message': '用户状态已更新'})


@app.route('/api/set_offline', methods=['POST'])
@login_required
def api_set_offline():
    """设置用户为离线状态"""
    user_status = UserStatus.query.filter_by(user_id=current_user.id).first()

    if user_status:
        was_online = user_status.is_online
        user_status.is_online = False
        user_status.last_offline_time = get_current_time(
        ).astimezone(timezone.utc).replace(tzinfo=None)
        db.session.commit()

        # 如果用户之前是在线的，通知好友
        if was_online:
            status_change_data = {
                'user_id': current_user.id,
                'username': current_user.username,
                'is_online': False,
                'last_seen': time_ago(get_current_time().astimezone(timezone.utc).replace(tzinfo=None))
            }
            notify_friends_about_status_change(
                current_user.id, status_change_data)

    return jsonify({'success': True, 'message': '用户状态已设置为离线'})


@app.route('/api/trending/daily')
def api_trending_daily():
    """获取每日热度排行API"""
    from chinese_time_utils import calculate_daily_trends
    daily_trends = calculate_daily_trends()

    # 准备返回数据
    trends_data = []
    for item_data in daily_trends:
        item = item_data.get('item') if isinstance(
            item_data, dict) else item_data.item
        score = item_data.get('score') if isinstance(
            item_data, dict) else item_data.score
        item_type = item_data.get('type') if isinstance(
            item_data, dict) else item_data.type

        trends_data.append({
            'type': item_type,
            'item': {
                'id': item.id,
                'title': item.title,
                'author': getattr(item, 'author', None).username if hasattr(item, 'author') else None,
            },
            'score': float(score) if score is not None else 0
        })

    return jsonify({'success': True, 'trends': trends_data})


@app.route('/api/users')
def api_users():
    """获取用户列表API"""
    users = User.query.all()
    users_data = []
    for user in users:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'bio': user.bio,
            'location': user.location,
            'website': user.website,
            'join_date': user.join_date.isoformat() if user.join_date else None,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'is_online': user.is_online if hasattr(user, 'is_online') else False,
        })

    return jsonify({'success': True, 'users': users_data})


@app.route('/api/messages/<recipient_username>')
@login_required
def api_get_messages(recipient_username):
    """获取与指定用户的新消息API"""
    from flask import request
    recipient = User.query.filter_by(
        username=recipient_username).first_or_404()

    # 获取最后时间戳参数
    last_timestamp_str = request.args.get('last_timestamp')
    last_timestamp = None
    if last_timestamp_str and last_timestamp_str != 'null':
        try:
            from datetime import datetime
            last_timestamp = datetime.fromisoformat(
                last_timestamp_str.replace('Z', '+00:00'))
        except ValueError:
            pass

    # 查询新消息
    query = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient.id)) |
        ((Message.sender_id == recipient.id) &
         (Message.recipient_id == current_user.id))
    )

    if last_timestamp:
        query = query.filter(Message.timestamp > last_timestamp)

    new_messages = query.order_by(Message.timestamp.asc()).all()

    # 构造返回数据
    messages_data = []
    for msg in new_messages:
        # 格式化时间戳
        timestamp_formatted = msg.timestamp.strftime('%Y-%m-%d %H:%M')

        # 构造附件URL
        attachment_url = None
        if msg.attachment_path:
            # 使用与模板函数相同的逻辑构造URL
            if msg.attachment_path.startswith(('http://', 'https://')):
                attachment_url = msg.attachment_path
            elif msg.attachment_path.startswith('/static/'):
                attachment_url = msg.attachment_path
            elif msg.attachment_path.startswith('uploads/'):
                attachment_url = f"/static/{msg.attachment_path}"
            else:
                attachment_url = f"/static/uploads/{msg.attachment_path}"

        # 设置消息发送者与当前用户的关系
        is_friend = False
        is_followed = False
        if msg.sender_id != current_user.id:
            # 检查是否是好友（互相关注）
            if current_user.is_following(msg.sender) and msg.sender.is_following(current_user):
                is_friend = True
            elif current_user.is_following(msg.sender):
                is_followed = True

        message_data = {
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender_id,
            'sender_username': msg.sender.username,
            'sender_avatar_url': get_avatar_url(msg.sender.avatar),
            'recipient_id': msg.recipient_id,
            'timestamp': msg.timestamp.isoformat(),
            'timestamp_formatted': timestamp_formatted,
            'is_read': msg.is_read,
            'is_friend': is_friend,
            'is_followed': is_followed,
            'attachment_path': msg.attachment_path,
            'attachment_filename': msg.attachment_filename,
            'attachment_type': msg.attachment_type,
            'attachment_url': attachment_url  # 包含附件URL
        }
        messages_data.append(message_data)

    return jsonify({'success': True, 'messages': messages_data})


@app.route('/mark_messages_read/<recipient_username>', methods=['POST'])
@login_required
def mark_messages_read(recipient_username):
    """标记与指定用户的未读消息为已读"""
    recipient = User.query.filter_by(
        username=recipient_username).first_or_404()

    # 更新与该用户相关的未读消息
    messages_to_update = Message.query.filter(
        Message.sender_id == recipient.id,
        Message.recipient_id == current_user.id,
        Message.is_read == False
    ).all()

    for message in messages_to_update:
        message.is_read = True

    db.session.commit()

    return jsonify({'success': True, 'updated_count': len(messages_to_update)})


@app.route('/api/message/<int:message_id>/edit', methods=['POST'])
@login_required
def edit_message_api(message_id):
    """编辑消息API"""
    message = Message.query.get_or_404(message_id)

    # 只能编辑自己的消息
    if message.sender_id != current_user.id:
        return jsonify({'success': False, 'error': '无权编辑此消息'}), 403

    data = request.get_json()
    new_content = data.get('content', '').strip()

    if new_content:
        message.content = new_content
        message.updated_at = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None)  # 添加更新时间字段
        db.session.commit()
        return jsonify({'success': True, 'message': '消息已更新'})
    else:
        return jsonify({'success': False, 'error': '消息内容不能为空'}), 400


@app.route('/api/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message_api(message_id):
    """删除消息API"""
    message = Message.query.get_or_404(message_id)

    # 只能删除自己的消息
    if message.sender_id != current_user.id:
        return jsonify({'success': False, 'error': '无权删除此消息'}), 403

    db.session.delete(message)
    db.session.commit()

    return jsonify({'success': True, 'message': '消息已删除'})


@app.route('/captcha')
def captcha():
    """生成验证码图片"""
    from io import BytesIO
    from flask import send_file
    from utils import generate_captcha, create_captcha_image

    # 生成随机验证码
    captcha_text = generate_captcha()

    # 保存到session以便验证
    session['captcha'] = captcha_text

    # 创建验证码图片
    img = create_captcha_image(captcha_text)

    # 将图片保存到内存中并返回
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')


if __name__ == '__main__':
    # 应用启动时自动检查并补充缺失日期的新闻
    def auto_fill_news_on_startup():
        """应用启动时自动填充缺失日期的新闻"""
        import threading
        from datetime import date, timedelta

        def fill_in_background():
            """在后台线程中执行"""
            try:
                with app.app_context():
                    from datetime import datetime
                    from sqlalchemy import func

                    # 检查从1月1日到今天，哪些日期没有新闻
                    start_date = date(2026, 1, 1)
                    today = date.today()

                    # 随机抽查几个日期，看看是否需要补充
                    missing_count = 0
                    for _ in range(10):  # 抽查10天
                        random_day = start_date + \
                            timedelta(days=random.randint(
                                0, (today - start_date).days))
                        day_news = News.query.filter(
                            func.date(News.timestamp) == random_day
                        ).count()
                        if day_news == 0:
                            missing_count += 1

                    # 如果超过30%的抽查日期没有新闻，则补充
                    if missing_count >= 3:
                        print(f"\n[自动补充] 检测到新闻数据不足，开始补充...")
                        from batch_scrape_news import auto_fill_missing_dates
                        auto_fill_missing_dates()
                    else:
                        print(f"\n[自动补充] 新闻数据充足，无需补充")
            except Exception as e:
                print(f"\n[自动补充] 检查失败: {e}")

        # 在后台线程执行，不阻塞启动
        t = threading.Thread(target=fill_in_background, daemon=True)
        t.start()

    # 执行自动补充
    auto_fill_news_on_startup()

    # 启动应用
    app.run(debug=True)
