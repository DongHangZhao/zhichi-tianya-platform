'''
Author: your name
Date: 2026-01-21 00:43:23
LastEditTime: 2026-01-21 00:43:23
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\verify_db_structure.py
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库结构 - 验证updated_at列是否已添加
"""

import sqlite3
import os

# 检查数据库文件
if os.path.exists('app.db'):
    db_path = 'app.db'
elif os.path.exists('database.db'):
    db_path = 'database.db'
else:
    print("未找到数据库文件")
    exit(1)

print(f"正在检查数据库: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table[0]}")

    # 检查messages表是否存在
    if ('messages',) in tables:
        print("\nmessages表结构:")
        cursor.execute("PRAGMA table_info(messages)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]}) - {col[5]}")

        # 检查updated_at列是否存在
        column_names = [col[1] for col in columns]
        if 'updated_at' in column_names:
            print("\n✓ updated_at列已成功添加到messages表")
        else:
            print("\n✗ updated_at列未找到")
    else:
        print("\nmessages表不存在")

except sqlite3.Error as e:
    print(f"数据库操作错误: {e}")

finally:
    conn.close()
