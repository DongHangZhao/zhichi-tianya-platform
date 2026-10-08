'''
Author: your name
Date: 2026-01-11 00:45:46
LastEditTime: 2026-01-11 00:45:46
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\initialize_builtin_users.py
'''
"""
初始化内置用户和头像
"""

import os
from app import app, db
from models import User


def initialize_builtin_users():
    """初始化内置用户和他们的头像"""
    with app.app_context():
        # 检查是否已有用户，避免重复初始化
        existing_users = User.query.count()
        if existing_users > 0:
            print("检测到已有用户，跳过初始化")
            return

        # 创建内置用户
        builtin_users = [
            {
                'username': 'admin',
                'email': 'admin@example.com',
                'password': 'admin123',
                'is_admin': True,
                'avatar': 'default_avatar_admin.png'  # 使用特定管理员头像
            },
            {
                'username': 'tianmi',
                'email': 'tianmi@example.com',
                'password': 'password123',
                'is_admin': False,
                'avatar': 'default_avatar_tianmi.png'
            },
            {
                'username': 'FallPetal',
                'email': 'fallpetal@example.com',
                'password': 'password123',
                'is_admin': False,
                'avatar': 'default_avatar_fallpetal.png'
            },
            {
                'username': 'zhangsan',
                'email': 'zhangsan@example.com',
                'password': 'password123',
                'is_admin': False,
                'avatar': 'default_avatar_zhangsan.png'
            },
            {
                'username': 'lisi',
                'email': 'lisi@example.com',
                'password': 'password123',
                'is_admin': False,
                'avatar': 'default_avatar_lisi.png'
            },
            {
                'username': 'tester',
                'email': 'tester@example.com',
                'password': 'test123',
                'is_admin': False,
                'avatar': 'default_avatar.png'
            }
        ]

        for user_data in builtin_users:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(
                username=user_data['username']).first()
            if not existing_user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    avatar=user_data['avatar']
                )
                user.set_password(user_data['password'])
                user.is_admin = user_data.get('is_admin', False)

                db.session.add(user)
                print(f"创建用户: {user_data['username']}")

        db.session.commit()
        print("内置用户初始化完成")


if __name__ == '__main__':
    initialize_builtin_users()
