'''
Author: your name
Date: 2026-04-10 20:37:38
LastEditTime: 2026-04-10 20:37:38
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\add_news_url_field.py
'''
"""
添加新闻URL字段的数据库迁移
"""

import os
from app import app, db
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def add_url_column():
    """添加url字段到news表"""
    with app.app_context():
        try:
            # 使用原生SQL添加列
            db.session.execute(db.text(
                "ALTER TABLE news ADD COLUMN url VARCHAR(500) DEFAULT ''"
            ))
            db.session.commit()
            print("✅ 成功添加 url 字段到 news 表")
        except Exception as e:
            if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
                print("ℹ️  url 字段已存在，跳过")
            else:
                print(f"❌ 添加字段失败: {e}")
                db.session.rollback()


if __name__ == '__main__':
    add_url_column()
