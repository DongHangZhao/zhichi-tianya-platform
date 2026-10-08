'''
Author: your name
Date: 2026-01-20 18:14:28
LastEditTime: 2026-01-20 18:14:28
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\migrate_comments_table.py
'''
"""
数据库迁移脚本：为comments表添加news_id列
"""

import sqlite3
import os
from models import db
from app import app

def migrate_comments_table():
    """
    为comments表添加news_id列
    """
    print("开始迁移comments表，添加news_id列...")
    
    # 检查列是否存在
    with app.app_context():
        # 使用底层SQLite连接检查表结构
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        
        if not os.path.exists(db_path):
            print(f"数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询表结构
        cursor.execute("PRAGMA table_info(comments)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print(f"当前comments表的列: {column_names}")
        
        # 检查news_id列是否存在
        if 'news_id' not in column_names:
            print("发现缺失的news_id列，正在添加...")
            
            try:
                # 添加news_id列
                cursor.execute("ALTER TABLE comments ADD COLUMN news_id INTEGER")
                
                # 如果需要，添加外键约束（SQLite中外键约束需要特殊启用）
                conn.commit()
                
                print("成功添加news_id列到comments表")
                
                # 验证更改
                cursor.execute("PRAGMA table_info(comments)")
                new_columns = cursor.fetchall()
                new_column_names = [column[1] for column in new_columns]
                
                print(f"更新后的comments表列: {new_column_names}")
                
                if 'news_id' in new_column_names:
                    print("✅ 迁移成功完成！")
                    return True
                else:
                    print("❌ 迁移可能失败，news_id列未找到")
                    return False
                    
            except sqlite3.Error as e:
                print(f"❌ 迁移失败: {e}")
                conn.rollback()
                return False
        else:
            print("✅ news_id列已存在于comments表中，无需迁移")
            return True
    
    conn.close()


def verify_migration():
    """
    验证迁移是否成功
    """
    print("\n验证迁移结果...")
    
    with app.app_context():
        db_path = app.config.get('SQLALCHEMY_DATABASE_URI').replace('sqlite:///', '')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(comments)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        
        print(f"comments表的列: {column_names}")
        
        # 检查所有预期的列
        expected_columns = ['post_id', 'video_id', 'news_id']
        missing_columns = [col for col in expected_columns if col not in column_names]
        
        if missing_columns:
            print(f"❌ 仍缺少以下列: {missing_columns}")
            return False
        else:
            print("✅ 所有预期的列都存在")
            return True
    
    conn.close()


if __name__ == "__main__":
    print("="*60)
    print("数据库迁移工具 - 为comments表添加news_id列")
    print("="*60)
    
    success = migrate_comments_table()
    
    if success:
        verify_migration()
        print("\n🎉 迁移完成！请重启应用程序以使更改生效。")
    else:
        print("\n❌ 迁移失败，请检查错误信息。")
    
    print("="*60)