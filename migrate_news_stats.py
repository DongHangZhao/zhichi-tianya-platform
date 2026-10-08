'''
Author: your name
Date: 2026-03-30 16:41:20
LastEditTime: 2026-03-30 16:41:20
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\migrate_news_stats.py
'''
"""
新闻统计功能数据库迁移脚本
添加 comments_count 字段和 operation_logs 表
"""

import sys
from sqlalchemy import text
from app import app, db
sys.path.append('.')


def migrate():
    """执行数据库迁移"""
    with app.app_context():
        print("开始数据库迁移...")

        # 1. 检查 news 表是否存在 comments_count 列
        print("\n1. 检查并添加 news.comments_count 列...")
        try:
            result = db.session.execute(text(
                "PRAGMA table_info(news)"
            )).fetchall()

            columns = [row[1] for row in result]

            if 'comments_count' not in columns:
                db.session.execute(text(
                    "ALTER TABLE news ADD COLUMN comments_count INTEGER DEFAULT 0"
                ))
                db.session.commit()
                print("   ✓ 已添加 comments_count 列")
            else:
                print("   ✓ comments_count 列已存在")
        except Exception as e:
            print(f"   ✗ 添加 comments_count 列失败：{e}")
            db.session.rollback()

        # 2. 创建 news_operation_logs 表
        print("\n2. 创建 news_operation_logs 表...")
        try:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS news_operation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id INTEGER NOT NULL,
                user_id INTEGER,
                operation_type VARCHAR(20) NOT NULL,
                old_value INTEGER,
                new_value INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(50),
                user_agent VARCHAR(200),
                FOREIGN KEY (news_id) REFERENCES news(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
            db.session.execute(text(create_table_sql))
            db.session.commit()
            print("   ✓ 已创建 news_operation_logs 表")
        except Exception as e:
            print(f"   ✗ 创建 news_operation_logs 表失败：{e}")
            db.session.rollback()

        # 3. 为现有新闻初始化评论数
        print("\n3. 初始化现有新闻的评论数...")
        try:
            init_sql = """
            UPDATE news 
            SET comments_count = (
                SELECT COUNT(*) FROM comments 
                WHERE comments.news_id = news.id
            )
            WHERE comments_count IS NULL OR comments_count = 0
            """
            result = db.session.execute(text(init_sql))
            db.session.commit()
            updated_count = result.rowcount
            print(f"   ✓ 已更新 {updated_count} 条新闻的评论数")
        except Exception as e:
            print(f"   ✗ 初始化评论数失败：{e}")
            db.session.rollback()

        print("\n✅ 数据库迁移完成！")
        print("\n新增功能:")
        print("  - news.comments_count: 记录每条评论的数量")
        print("  - news_operation_logs: 记录所有操作日志（查看、点赞、评论）")
        print("\n所有更改都将:")
        print("  ✓ 实时更新到数据库")
        print("  ✓ 记录详细的操作日志")
        print("  ✓ 包含操作时间、IP 地址、用户代理等信息")


if __name__ == '__main__':
    migrate()
