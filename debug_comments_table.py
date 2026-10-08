'''
Author: your name
Date: 2026-01-20 22:39:27
LastEditTime: 2026-01-20 22:39:28
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\debug_comments_table.py
'''
"""
调试评论表结构问题
"""
import sqlite3
from app import app, db
from models import Comment


def debug_comments_table():
    print("=== 评论表结构调试 ===")

    with app.app_context():
        # 检查SQLAlchemy模型定义
        print("\n1. SQLAlchemy模型定义:")
        print(
            f"   Comment.__table__.columns: {[col.name for col in Comment.__table__.columns]}")

        # 直接查询数据库表结构
        print("\n2. 数据库表结构:")
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(comments);")
        columns = cursor.fetchall()
        print("   数据库中的列:")
        for col in columns:
            print(f"     {col}")
        conn.close()

        # 尝试查询测试
        print("\n3. 测试查询:")
        try:
            # 测试是否可以访问news_id列
            sample_comment = Comment.query.first()
            if sample_comment:
                print(f"   样本评论ID: {sample_comment.id}")
                print(
                    f"   样本评论news_id: {getattr(sample_comment, 'news_id', 'NOT FOUND')}")
                print(
                    f"   样本评论post_id: {getattr(sample_comment, 'post_id', 'NOT FOUND')}")
                print(
                    f"   样本评论video_id: {getattr(sample_comment, 'video_id', 'NOT FOUND')}")
            else:
                print("   没有找到任何评论记录")
        except Exception as e:
            print(f"   查询测试失败: {e}")

        print("\n4. 尝试重现错误:")
        try:
            # 尝试执行导致错误的查询
            comments = Comment.query.filter_by(post_id=1).all()
            print(f"   成功查询到 {len(comments)} 条评论")
        except Exception as e:
            print(f"   查询失败: {e}")


if __name__ == "__main__":
    debug_comments_table()
