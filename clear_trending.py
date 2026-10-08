'''
Author: your name
Date: 2026-04-11 23:16:07
LastEditTime: 2026-04-11 23:16:07
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\clear_trending.py
'''
# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'users.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("清空trending表...")
cursor.execute("DELETE FROM trending")
conn.commit()

count = cursor.execute("SELECT COUNT(*) FROM trending").fetchone()[0]
print(f"trending表现有数据: {count} 条")

conn.close()
print("完成")
