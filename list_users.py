'''
Author: your name
Date: 2026-01-11 00:59:23
LastEditTime: 2026-01-11 00:59:23
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\list_users.py
'''
"""
列出所有用户及其头像信息
"""
from app import app
from models import User


def list_all_users():
    """列出所有用户的用户名和头像"""
    with app.app_context():
        users = User.query.all()
        print("数据库中的所有用户:")
        print("-" * 40)
        for user in users:
            print(f"{user.username}: {user.avatar}")


if __name__ == '__main__':
    list_all_users()