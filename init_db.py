'''
Author: your name
Date: 2026-01-19 03:49:25
LastEditTime: 2026-01-19 03:49:25
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\init_db.py
'''
import sqlite3
from app import app, db
import os

print('初始化数据库...')
with app.app_context():
    # 创建所有表
    db.create_all()
    print('数据库表已创建')

conn = sqlite3.connect('app.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('数据库表:', tables)

cursor.execute('PRAGMA table_info(comments)')
rows = cursor.fetchall()
print('Comments表结构:')
for row in rows:
    print(row)

# 检查News表
cursor.execute('PRAGMA table_info(news)')
news_rows = cursor.fetchall()
print('News表结构:')
for row in news_rows:
    print(row)

conn.close()
