'''
Author: your name
Date: 2026-01-11 20:41:13
LastEditTime: 2026-01-11 20:41:13
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\migrate_posts_table.py
'''
"""
数据库迁移脚本：为posts表添加video_url字段
"""
import sqlite3
import os

def migrate_posts_table():
    """为posts表添加video_url字段"""
    # 数据库文件路径
    db_path = os.path.join('database', 'users.db')
    
    # 如果数据库文件不存在，检查当前目录
    if not os.path.exists(db_path):
        db_path = 'users.db'
        if not os.path.exists(db_path):
            print("未找到数据库文件，尝试使用默认路径 instance/users.db")
            db_path = os.path.join('instance', 'users.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else os.makedirs('instance', exist_ok=True)
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查posts表是否已存在video_url列
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'video_url' in columns:
            print("video_url列已存在，无需迁移")
            conn.close()
            return
        
        # 为posts表添加video_url列
        cursor.execute("ALTER TABLE posts ADD COLUMN video_url TEXT DEFAULT NULL")
        
        # 提交更改
        conn.commit()
        print("成功为posts表添加video_url列")
        
        # 验证更改
        cursor.execute("PRAGMA table_info(posts)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"posts表当前列: {columns}")
        
        conn.close()
        print("数据库迁移完成")
        
    except sqlite3.Error as e:
        print(f"数据库操作错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    migrate_posts_table()