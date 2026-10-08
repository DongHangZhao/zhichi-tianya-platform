'''
Author: your name
Date: 2026-01-12 00:12:43
LastEditTime: 2026-01-12 00:12:43
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\initialize_user_status.py
'''
from app import app, db
from models import User, UserStatus
from datetime import datetime, timedelta
import random


def initialize_user_status():
    """为现有用户初始化状态数据"""
    with app.app_context():
        users = User.query.all()
        for user in users:
            # 查找或创建用户状态记录
            user_status = UserStatus.query.filter_by(user_id=user.id).first()
            if not user_status:
                # 随机决定用户是否在线，大部分用户设为离线
                is_online = random.choice([True, False]) if user.username == 'admin' else False
                
                if is_online:
                    last_online_time = datetime.utcnow()
                    last_offline_time = None
                else:
                    # 随机设置最后在线时间为过去几天内的某个时间
                    days_ago = random.randint(0, 7)
                    last_seen_time = datetime.utcnow() - timedelta(days=days_ago, 
                                                                 hours=random.randint(0, 23),
                                                                 minutes=random.randint(0, 59))
                    last_online_time = last_seen_time
                    last_offline_time = last_seen_time
                
                status = UserStatus(
                    user_id=user.id,
                    is_online=is_online,
                    last_online_time=last_online_time,
                    last_offline_time=last_offline_time
                )
                db.session.add(status)
                print(f"为用户 {user.username} 设置初始状态: {'在线' if is_online else '离线'}")
        
        db.session.commit()
        print("用户状态初始化完成")


if __name__ == "__main__":
    initialize_user_status()