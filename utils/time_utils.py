"""
时间处理工具模块
统一处理时区和时间显示
"""
from datetime import datetime, timezone, timedelta
import pytz


def get_local_timezone():
    """
    获取本地时区（中国标准时间 UTC+8）
    """
    return pytz.timezone('Asia/Shanghai')


def utc_to_local(utc_dt):
    """
    将UTC时间转换为本地时间（中国标准时间）
    """
    if utc_dt is None:
        return None

    # 如果时间没有时区信息，假设为UTC时间
    if utc_dt.tzinfo is None:
        utc_dt = utc_dt.replace(tzinfo=timezone.utc)

    # 转换到本地时区
    local_tz = get_local_timezone()
    local_dt = utc_dt.astimezone(local_tz)

    return local_dt


def local_to_utc(local_dt):
    """
    将本地时间转换为UTC时间
    """
    if local_dt is None:
        return None

    # 如果时间没有时区信息，假设为本地时间
    if local_dt.tzinfo is None:
        local_tz = get_local_timezone()
        local_dt = local_tz.localize(local_dt)

    # 转换到UTC
    utc_dt = local_dt.astimezone(timezone.utc)

    return utc_dt


def get_current_time():
    """
    获取当前本地时间
    """
    utc_now = datetime.now(timezone.utc)
    return utc_to_local(utc_now)


def format_datetime_local(dt, format_str='%Y-%m-%d %H:%M:%S'):
    """
    格式化时间为本地时间字符串
    """
    if dt is None:
        return "未知时间"

    local_dt = utc_to_local(dt)
    return local_dt.strftime(format_str)


def format_datetime_china_friendly(dt):
    """
    格式化时间为中文友好格式
    """
    if dt is None:
        return "未知时间"

    local_dt = utc_to_local(dt)
    now = get_current_time()

    # 计算时间差
    diff = now - local_dt

    days = diff.days
    seconds = diff.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if days > 7:  # 超过一周，显示具体日期
        return local_dt.strftime('%m月%d日 %H:%M')
    elif days > 1:  # 超过一天，显示几天前
        return f"{days}天前"
    elif days == 1:  # 一天前
        return f"{days}天前"
    elif hours > 1:  # 几小时前
        return f"{hours}小时前"
    elif hours == 1:  # 1小时前
        return "1小时前"
    elif minutes > 1:  # 几分钟前
        return f"{minutes}分钟前"
    else:  # 一分钟内
        return "刚刚"


def get_start_of_day(dt):
    """
    获取指定日期的开始时间（00:00:00）
    """
    local_dt = utc_to_local(dt)
    start_of_day = local_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_to_utc(start_of_day)


def get_end_of_day(dt):
    """
    获取指定日期的结束时间（23:59:59）
    """
    local_dt = utc_to_local(dt)
    end_of_day = local_dt.replace(
        hour=23, minute=59, second=59, microsecond=999999)
    return local_to_utc(end_of_day)
