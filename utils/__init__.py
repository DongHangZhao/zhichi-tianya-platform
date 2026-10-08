import os
import uuid
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import hashlib
import secrets
from io import BytesIO
import string


def generate_filename(filename):
    """生成唯一文件名"""
    ext = os.path.splitext(filename)[1]
    unique_filename = str(uuid.uuid4()) + ext
    return unique_filename


def save_image(image, upload_folder, size=(300, 300)):
    """保存并压缩图片"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = generate_filename(image.filename)
    filepath = os.path.join(upload_folder, filename)

    # 检查文件类型是否为支持的图像格式
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    file_ext = os.path.splitext(image.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValueError(f"不支持的图像格式: {file_ext}")

    # 确保从文件开头读取
    image.seek(0)

    # 直接使用上传的图像文件，不做额外处理
    import io
    from PIL import Image as PILImage

    # 使用BytesIO直接处理原始上传的图像
    image_bytes = image.read()
    image_stream = io.BytesIO(image_bytes)

    try:
        # 直接打开图像
        with PILImage.open(image_stream) as img:
            original_format = img.format or 'JPEG'  # 保留原始格式信息

            # 检查图像是否损坏
            try:
                img.load()
            except Exception as e:
                raise ValueError(f"图像文件已损坏: {str(e)}")

            # 如果是透明背景的图像，转换为带白色背景的RGB图像
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = PILImage.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img_rgba = img.convert('RGBA')
                    background.paste(img_rgba, mask=img_rgba.split()[-1])
                elif img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            # 调整大小
            img.thumbnail(size, PILImage.Resampling.LANCZOS)

            # 保存图像
            img.save(filepath, 'JPEG', optimize=True, quality=85)

        return filename
    except PILImage.UnidentifiedImageError:
        # 如果PIL无法识别图像，则尝试修复
        # 将原始数据写入临时文件再尝试处理
        import tempfile
        import os as os_module

        image.seek(0)  # 重置文件指针
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file.write(image_bytes)
            temp_filename = temp_file.name

        try:
            with PILImage.open(temp_filename) as img:
                original_format = img.format or 'JPEG'

                # 检查图像是否损坏
                try:
                    img.load()
                except Exception as e:
                    raise ValueError(f"图像文件已损坏: {str(e)}")

                # 如果是透明背景的图像，转换为带白色背景的RGB图像
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = PILImage.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img_rgba = img.convert('RGBA')
                        background.paste(img_rgba, mask=img_rgba.split()[-1])
                    elif img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # 调整大小
                img.thumbnail(size, PILImage.Resampling.LANCZOS)

                # 保存图像
                img.save(filepath, 'JPEG', optimize=True, quality=85)

            return filename
        except Exception as e:
            raise ValueError(f"无法处理图像文件: {str(e)}")
        finally:
            # 清理临时文件
            if os_module.path.exists(temp_filename):
                os_module.unlink(temp_filename)


def save_file(file, upload_folder):
    """保存文件"""
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    filename = generate_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return filename


def save_attachment(attachment_file, upload_folder, max_size=1024*1024*1024):  # 1GB
    """
    保存附件文件，支持多种文件类型
    max_size: 最大文件大小（字节），默认1GB
    """
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # 检查文件大小
    attachment_file.seek(0, os.SEEK_END)  # 移动到文件末尾
    file_size = attachment_file.tell()  # 获取当前位置（即文件大小）
    attachment_file.seek(0)  # 重置文件指针到开始位置

    if file_size > max_size:
        raise ValueError(f"文件过大，最大允许 {max_size/(1024*1024):.1f}MB")

    # 生成安全的文件名
    filename = generate_filename(attachment_file.filename)
    filepath = os.path.join(upload_folder, filename)

    # 保存文件
    attachment_file.save(filepath)

    # 获取文件扩展名以确定类型
    file_ext = os.path.splitext(attachment_file.filename)[1].lower()

    # 确定附件类型
    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        attachment_type = 'image'
    elif file_ext in ['.mp4', '.avi', '.mov', '.wmv', '.mkv', '.webm']:
        attachment_type = 'video'
    elif file_ext in ['.mp3', '.wav', '.ogg', '.flac']:
        attachment_type = 'audio'
    elif file_ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx']:
        attachment_type = 'document'
    elif file_ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
        attachment_type = 'archive'
    else:
        attachment_type = 'file'

    return filename, attachment_type


def format_datetime(value, format='%Y-%m-%d %H:%M'):
    """格式化日期时间"""
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return value.strftime(format)


def time_ago(dt):
    """计算时间差（例如：几分钟前）"""
    now = datetime.now()
    diff = now - dt

    if diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600}小时前"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60}分钟前"
    else:
        return "刚刚"


def calculate_trend_score(item):
    """计算热度分数"""
    # 简单的热度算法：基于点赞数、评论数、发布时间
    now = datetime.now()
    time_diff_hours = (now - item.timestamp).total_seconds() / 3600

    # 越新的内容权重越高
    time_weight = max(0, 24 - time_diff_hours) / 24
    if time_weight < 0:
        time_weight = 0.1  # 最低权重

    # 计算基础分数
    base_score = 0
    if hasattr(item, 'likes_count'):
        base_score += item.likes_count * 2
    if hasattr(item, 'comments_count'):
        base_score += item.comments_count
    if hasattr(item, 'views'):
        base_score += item.views * 0.1

    # 应用时间权重
    trend_score = base_score * time_weight
    return trend_score


def calculate_daily_trends():
    """计算每日热度排行"""
    from models import Post, Video, News
    from datetime import datetime, timedelta

    # 获取今天的数据
    today_start = datetime.now().date()
    today_start = datetime.combine(today_start, datetime.min.time())

    # 获取今天的帖子、视频和新闻
    daily_posts = Post.query.filter(Post.timestamp >= today_start).all()
    daily_videos = Video.query.filter(Video.timestamp >= today_start).all()
    daily_news = News.query.filter(News.timestamp >= today_start).all()

    # 计算热度并排序
    all_items = []

    for post in daily_posts:
        all_items.append({
            'type': 'post',
            'item': post,
            'score': calculate_trend_score(post)
        })

    for video in daily_videos:
        all_items.append({
            'type': 'video',
            'item': video,
            'score': calculate_trend_score(video)
        })

    for news in daily_news:
        all_items.append({
            'type': 'news',
            'item': news,
            'score': calculate_trend_score(news)
        })

    # 按热度分数排序
    all_items.sort(key=lambda x: x['score'], reverse=True)
    return all_items


def calculate_weekly_trends():
    """计算每周热度排行"""
    from models import Post, Video, News
    from datetime import datetime, timedelta

    # 获取本周的数据
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())  # 本周周一
    week_start = datetime.combine(week_start, datetime.min.time())

    # 获取本周的帖子、视频和新闻
    weekly_posts = Post.query.filter(Post.timestamp >= week_start).all()
    weekly_videos = Video.query.filter(Video.timestamp >= week_start).all()
    weekly_news = News.query.filter(News.timestamp >= week_start).all()

    # 计算热度并排序
    all_items = []

    for post in weekly_posts:
        all_items.append({
            'type': 'post',
            'item': post,
            'score': calculate_trend_score(post)
        })

    for video in weekly_videos:
        all_items.append({
            'type': 'video',
            'item': video,
            'score': calculate_trend_score(video)
        })

    for news in weekly_news:
        all_items.append({
            'type': 'news',
            'item': news,
            'score': calculate_trend_score(news)
        })

    # 按热度分数排序
    all_items.sort(key=lambda x: x['score'], reverse=True)
    return all_items


def calculate_monthly_trends():
    """计算每月热度排行"""
    from models import Post, Video, News
    from datetime import datetime, timedelta

    # 获取本月的数据
    today = datetime.now().date()
    month_start = today.replace(day=1)  # 本月第一天
    month_start = datetime.combine(month_start, datetime.min.time())

    # 获取本月的帖子、视频和新闻
    monthly_posts = Post.query.filter(Post.timestamp >= month_start).all()
    monthly_videos = Video.query.filter(Video.timestamp >= month_start).all()
    monthly_news = News.query.filter(News.timestamp >= month_start).all()

    # 计算热度并排序
    all_items = []

    for post in monthly_posts:
        all_items.append({
            'type': 'post',
            'item': post,
            'score': calculate_trend_score(post)
        })

    for video in monthly_videos:
        all_items.append({
            'type': 'video',
            'item': video,
            'score': calculate_trend_score(video)
        })

    for news in monthly_news:
        all_items.append({
            'type': 'news',
            'item': news,
            'score': calculate_trend_score(news)
        })

    # 按热度分数排序
    all_items.sort(key=lambda x: x['score'], reverse=True)
    return all_items


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """验证密码"""
    return hash_password(password) == hashed


def sanitize_html(html_content):
    """清理HTML内容（防止XSS攻击）"""
    # 这里应该使用更完整的HTML清理库，如bleach
    # 简单示例：替换一些危险标签
    dangerous_tags = ['script', 'iframe', 'object', 'embed', 'form', 'input']

    clean_content = html_content
    for tag in dangerous_tags:
        clean_content = clean_content.replace(f'<{tag}', f'&lt;{tag}')
        clean_content = clean_content.replace(f'</{tag}', f'&lt;/{tag}>')

    return clean_content


def validate_username(username):
    """验证用户名"""
    if len(username) < 2 or len(username) > 20:
        return False
    # 只允许字母、数字、下划线和汉字
    import re
    pattern = r'^[\w\u4e00-\u9fff]+$'
    return bool(re.match(pattern, username))


def validate_email(email):
    """验证邮箱格式"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generate_avatar_color(username):
    """根据用户名生成默认头像颜色"""
    if not username:
        return '#007bff'  # 默认蓝色

    # 使用用户名的哈希值来生成颜色
    hash_value = hash(username) % 0xFFFFFF
    color = f'#{hash_value:06x}'
    return color


def generate_captcha():
    """生成验证码"""
    # 生成4位随机数字验证码
    captcha = ''.join([str(secrets.randbelow(10)) for _ in range(4)])
    return captcha


def create_captcha_image(captcha_text):
    """创建验证码图像"""
    # 创建图像
    width, height = 120, 40
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 添加一些干扰线
    for _ in range(5):
        x1 = secrets.randbelow(width)
        y1 = secrets.randbelow(height)
        x2 = secrets.randbelow(width)
        y2 = secrets.randbelow(height)
        draw.line([(x1, y1), (x2, y2)], fill=(secrets.randbelow(255),
                  secrets.randbelow(255), secrets.randbelow(255)), width=1)

    # 尝试使用字体，如果找不到则使用默认字体
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        try:
            font = ImageFont.truetype("simhei.ttf", 24)  # 黑体
        except:
            try:
                font = ImageFont.truetype("msyh.ttc", 24)  # 微软雅黑
            except:
                font = ImageFont.load_default()  # 默认字体

    # 计算文本位置
    bbox = draw.textbbox((0, 0), captcha_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 添加文本
    draw.text((x, y), captcha_text, fill=(0, 0, 0), font=font)

    # 添加一些随机点
    for _ in range(50):
        x = secrets.randbelow(width)
        y = secrets.randbelow(height)
        draw.point((x, y), fill=(secrets.randbelow(255),
                   secrets.randbelow(255), secrets.randbelow(255)))

    return image  # 返回PIL图像对象而不是BytesIO


def get_recent_contacts(user, limit=10):
    """
    获取最近联系人列表，区分已互相关注和未互相关注的用户
    返回格式：[{user, is_mutual, latest_message}, ...]
    """
    from models import Message, User, db

    # 获取与当前用户通信过的所有用户，按最新消息时间排序
    # 查询接收和发送的消息，获取唯一的联系人
    sent_messages = db.session.query(Message)\
        .filter(Message.sender_id == user.id)\
        .order_by(Message.timestamp.desc()).all()

    received_messages = db.session.query(Message)\
        .filter(Message.recipient_id == user.id)\
        .order_by(Message.timestamp.desc()).all()

    # 合并消息列表并按时间排序
    all_messages = sorted(sent_messages + received_messages,
                          key=lambda m: m.timestamp, reverse=True)

    contacts = []
    processed_usernames = set()

    for msg in all_messages:
        if len(contacts) >= limit:
            break

        # 确定联系人（发送者或接收者，但不是当前用户）
        contact_user = None
        if msg.sender_id == user.id:
            contact_user = User.query.get(msg.recipient_id)
        else:
            contact_user = User.query.get(msg.sender_id)

        if contact_user and contact_user.username not in processed_usernames:
            # 检查是否互相关注
            is_mutual = user.is_following(
                contact_user) and contact_user.is_following(user)

            contacts.append({
                'user': contact_user,
                'is_mutual': is_mutual,
                'latest_message': msg
            })

            processed_usernames.add(contact_user.username)

    return contacts
