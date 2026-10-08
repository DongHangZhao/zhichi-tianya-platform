'''
Author: your name
Date: 2026-03-15 02:40:56
LastEditTime: 2026-03-15 02:40:56
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\clear_news_data.py
'''
"""
清空所有新闻数据
用于清理测试数据和假数据
"""

from app import app
from models import db, News


def clear_all_news():
    """清空所有新闻数据"""
    with app.app_context():
        # 删除所有新闻
        news_count = News.query.count()
        print(f"准备删除 {news_count} 条新闻...")

        # 删除所有新闻记录
        News.query.delete()
        db.session.commit()

        print(f"✓ 已删除所有 {news_count} 条新闻")
        print("✓ 数据库已清空")

        # 验证
        remaining = News.query.count()
        print(f"✓ 剩余新闻数：{remaining}")


if __name__ == '__main__':
    confirm = input("⚠️ 警告：此操作将删除所有新闻数据！输入 'yes' 确认执行：")
    if confirm.lower() == 'yes':
        clear_all_news()
        print("\n✅ 清空完成！")
    else:
        print("\n❌ 操作已取消")
