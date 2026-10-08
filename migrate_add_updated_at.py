'''
Author: your name
Date: 2026-01-21 00:42:25
LastEditTime: 2026-01-21 00:42:25
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\migrate_add_updated_at.py
'''
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加updated_at字段到messages表
"""

import os
from app import app
import sqlite3

# 数据库路径
# 先尝试app.db，如果不存在则尝试database.db
if os.path.exists('app.db'):
    db_path = 'app.db'
elif os.path.exists('database.db'):
    db_path = 'database.db'
else:
    db_path = 'app.db'  # 默认使用app.db

print(f"正在更新数据库: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 检查updated_at列是否存在
    cursor.execute("PRAGMA table_info(messages)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'updated_at' in columns:
        print("updated_at列已存在，无需更新")
    else:
        # 添加updated_at列
        cursor.execute(
            "ALTER TABLE messages ADD COLUMN updated_at TIMESTAMP NULL")
        print("已成功添加updated_at列到messages表")

    # 提交更改
    conn.commit()
    print("数据库更新完成！")

except sqlite3.Error as e:
    print(f"数据库操作错误: {e}")
    conn.rollback()

except Exception as e:
    print(f"发生错误: {e}")

finally:
    conn.close()
    print("数据库连接已关闭")
