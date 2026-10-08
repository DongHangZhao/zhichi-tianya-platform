'''
Time utilities for Chinese timezone
Handles datetime conversions for China Standard Time (CST, UTC+8)
'''
from datetime import datetime, timezone, timedelta
from utils.time_utils import get_current_time


def get_local_time(dt):
    """
    将UTC时间转换为本地时间
    默认使用中国标准时间(CST, UTC+8)
    """
    if dt is None:
        return None

    # 如果dt是naive datetime（不带时区信息），假设它是UTC时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # 中国标准时间是UTC+8
    cst_offset = timedelta(hours=8)
    cst_tz = timezone(cst_offset)

    # 转换为本地时区（中国标准时间）
    local_dt = dt.astimezone(cst_tz)

    return local_dt


def get_file_type(filepath):
    """
    根据文件扩展名判断文件类型
    """
    import os
    _, ext = os.path.splitext(filepath.lower())

    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    video_extensions = ['.mp4', '.mov', '.avi', '.wmv',
                        '.mkv', '.webm', '.flv', '.m4v', '.3gp', '.mpg', '.mpeg']
    audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac']
    archive_extensions = ['.zip', '.rar', '.7z', '.tar', '.gz', '.tgz', '.bz2']

    if ext in image_extensions:
        return 'image'
    elif ext in video_extensions:
        return 'video'
    elif ext in audio_extensions:
        return 'audio'
    elif ext in archive_extensions:
        return 'archive'
    else:
        return 'document'


def check_ffmpeg_available():
    """
    检查系统是否安装了FFmpeg
    """
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def save_attachment(file, upload_folder):
    """
    保存附件文件，如果是视频文件且不是MP4格式，则转换为MP4
    """
    import os
    import uuid
    from werkzeug.utils import secure_filename

    # 获取原始文件扩展名
    original_filename = secure_filename(file.filename)
    name, ext = os.path.splitext(original_filename)

    # 检查是否为视频文件
    video_extensions = ['.mov', '.avi', '.wmv', '.mkv',
                        '.webm', '.flv', '.m4v', '.3gp', '.mpg', '.mpeg']

    if ext.lower() in video_extensions:
        # 检查FFmpeg是否可用
        ffmpeg_available = check_ffmpeg_available()

        if ffmpeg_available:
            # 生成唯一文件名
            unique_filename = f"{str(uuid.uuid4())}.mp4"
            filepath = os.path.join(upload_folder, unique_filename)

            # 临时保存上传的文件
            temp_filepath = os.path.join(
                upload_folder, f"{str(uuid.uuid4())}{ext}")
            file.save(temp_filepath)

            try:
                # 使用FFmpeg将视频转换为MP4格式
                import subprocess
                result = subprocess.run([
                    'ffmpeg',
                    '-i', temp_filepath,  # 输入文件
                    '-vcodec', 'libx264',  # 视频编码器
                    '-acodec', 'aac',      # 音频编码器
                    '-strict', 'experimental',
                    '-b:a', '128k',        # 音频比特率
                    '-movflags', 'faststart',  # 优化MP4文件以支持流播放
                    filepath               # 输出文件
                ], check=True, capture_output=True, text=True)

                # 删除临时文件
                os.remove(temp_filepath)

                return unique_filename, 'video'
            except subprocess.CalledProcessError:
                # 如果转换失败，保留原始格式
                os.remove(temp_filepath)
                unique_filename = f"{str(uuid.uuid4())}{ext}"
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                return unique_filename, 'video'
            except FileNotFoundError:
                # 如果系统没有安装ffmpeg，保留原始格式
                os.remove(temp_filepath)
                unique_filename = f"{str(uuid.uuid4())}{ext}"
                filepath = os.path.join(upload_folder, unique_filename)
                file.save(filepath)
                return unique_filename, 'video'
        else:
            # 如果FFmpeg不可用，保留原始格式
            unique_filename = f"{str(uuid.uuid4())}{ext}"
            filepath = os.path.join(upload_folder, unique_filename)
            file.save(filepath)
            return unique_filename, 'video'
    else:
        # 非视频文件，直接保存
        unique_filename = f"{str(uuid.uuid4())}{ext}"
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)

        # 确定文件类型
        file_type = get_file_type(filepath)
        return unique_filename, file_type


def time_ago(dt):
    """
    计算时间差，返回多久前的描述
    """
    if dt is None:
        return "未知时间"

    # 如果dt是naive datetime（不带时区信息），假设它是UTC时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # 中国标准时间是UTC+8
    cst_offset = timedelta(hours=8)
    cst_tz = timezone(cst_offset)

    # 转换为本地时区（中国标准时间）
    local_dt = dt.astimezone(cst_tz)
    now_local = datetime.now(cst_tz)

    diff = now_local - local_dt

    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30.44  # 平均月份天数
    years = days / 365.25  # 考虑闰年

    if years >= 1:
        return f"{int(years)}年前"
    elif months >= 1:
        return f"{int(months)}个月前"
    elif weeks >= 1:
        return f"{int(weeks)}周前"
    elif days >= 1:
        return f"{int(days)}天前"
    elif hours >= 1:
        return f"{int(hours)}小时前"
    elif minutes >= 1:
        return f"{int(minutes)}分钟前"
    else:
        return "刚刚"


def format_datetime_china(dt):
    """
    格式化日期时间为中文显示格式（中国标准时间）
    """
    if dt is None:
        return "未知时间"

    # 如果dt是naive datetime（不带时区信息），假设它是UTC时间
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    # 中国标准时间是UTC+8
    cst_offset = timedelta(hours=8)
    cst_tz = timezone(cst_offset)

    # 转换为本地时区（中国标准时间）
    local_dt = dt.astimezone(cst_tz)

    # 返回格式化的日期时间
    return local_dt.strftime('%Y-%m-%d %H:%M')


def calculate_trend_score(likes_count, views, comments_count, age_hours):
    """
    计算热度分数
    基于点赞数、浏览数、评论数和内容年龄
    """
    # 基础分数计算
    base_score = (likes_count * 3) + (views * 0.5) + (comments_count * 2)

    # 考虑时间衰减因子
    # 较新的内容应该有更高的权重
    decay_factor = max(0.1, 24.0 / (age_hours + 1))  # 随着时间推移递减

    # 最终得分
    final_score = base_score * decay_factor
    return round(final_score, 2)


def calculate_daily_trends():
    """
    计算每日热度排行
    """
    from models import News, Post, Video
    from datetime import datetime, timedelta
    from app import db
    import math

    # 获取今天的数据
    today = get_current_time().date()
    yesterday = today - timedelta(days=1)

    # 获取所有类型的项目
    items_with_scores = []

    # 新闻项目
    news_items = News.query.filter(
        db.func.date(News.timestamp) == today
    ).all()

    for item in news_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, len(item.news_comments), age_hours)
        items_with_scores.append({
            'type': 'news',
            'item': item,
            'score': score
        })

    # 帖子项目
    post_items = Post.query.filter(
        db.func.date(Post.timestamp) == today
    ).all()

    for item in post_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, getattr(item, 'views', 0) or 0, item.comments_count, age_hours)
        # item.likes_count, item.views or 0, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'post',
            'item': item,
            'score': score
        })

    # 视频项目
    video_items = Video.query.filter(
        db.func.date(Video.timestamp) == today
    ).all()

    for item in video_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'video',
            'item': item,
            'score': score
        })

    # 按分数降序排序
    items_with_scores.sort(key=lambda x: x['score'], reverse=True)

    return items_with_scores


def calculate_weekly_trends():
    """
    计算每周热度排行
    """
    from models import News, Post, Video
    from datetime import datetime, timedelta
    import math

    # 获取本周的数据（最近7天）
    week_ago = get_current_time().astimezone(
        timezone.utc).replace(tzinfo=None) - timedelta(days=7)

    # 获取所有类型的项目
    items_with_scores = []

    # 新闻项目
    news_items = News.query.filter(News.timestamp >= week_ago).all()

    for item in news_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, len(item.news_comments), age_hours)
        items_with_scores.append({
            'type': 'news',
            'item': item,
            'score': score
        })

    # 帖子项目
    post_items = Post.query.filter(Post.timestamp >= week_ago).all()

    for item in post_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views or 0, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'post',
            'item': item,
            'score': score
        })

    # 视频项目
    video_items = Video.query.filter(Video.timestamp >= week_ago).all()

    for item in video_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'video',
            'item': item,
            'score': score
        })

    # 按分数降序排序
    items_with_scores.sort(key=lambda x: x['score'], reverse=True)

    return items_with_scores


def calculate_monthly_trends():
    """
    计算每月热度排行
    """
    from models import News, Post, Video
    from datetime import datetime, timedelta
    import math

    # 获取本月的数据（最近30天）
    month_ago = get_current_time().astimezone(
        timezone.utc).replace(tzinfo=None) - timedelta(days=30)

    # 获取所有类型的项目
    items_with_scores = []

    # 新闻项目
    news_items = News.query.filter(News.timestamp >= month_ago).all()

    for item in news_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, len(item.news_comments), age_hours)
        items_with_scores.append({
            'type': 'news',
            'item': item,
            'score': score
        })

    # 帖子项目
    post_items = Post.query.filter(Post.timestamp >= month_ago).all()

    for item in post_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views or 0, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'post',
            'item': item,
            'score': score
        })

    # 视频项目
    video_items = Video.query.filter(Video.timestamp >= month_ago).all()

    for item in video_items:
        age = get_current_time().astimezone(
            timezone.utc).replace(tzinfo=None) - item.timestamp
        age_hours = age.total_seconds() / 3600
        score = calculate_trend_score(
            item.likes_count, item.views, item.comments_count, age_hours)
        items_with_scores.append({
            'type': 'video',
            'item': item,
            'score': score
        })

    # 按分数降序排序
    items_with_scores.sort(key=lambda x: x['score'], reverse=True)

    return items_with_scores
