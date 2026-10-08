'''
Author: your name
Date: 2026-01-20 22:41:10
LastEditTime: 2026-01-20 22:41:11
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\test_post_detail.py
'''
"""
测试post_detail函数
"""
import sqlite3
from app import app, db
from models import Post, Comment


def test_post_detail_query():
    print("=== 测试post_detail查询 ===")

    with app.app_context():
        # 检查是否有帖子
        posts = Post.query.all()
        print(f"数据库中帖子总数: {len(posts)}")

        if posts:
            # 测试访问第一个帖子
            test_post = posts[0]
            print(f"测试帖子ID: {test_post.id}, 标题: {test_post.title}")

            # 尝试执行导致错误的查询
            try:
                comments = Comment.query.filter_by(
                    post_id=test_post.id).order_by(Comment.timestamp.asc()).all()
                print(f"   成功查询到帖子 {test_post.id} 的 {len(comments)} 条评论")

                # 显示评论信息
                for comment in comments:
                    print(
                        f"   - 评论ID: {comment.id}, 内容长度: {len(comment.content)}, 时间: {comment.timestamp}")

            except Exception as e:
                print(f"   查询失败: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("   没有找到任何帖子")

        # 检查评论表是否有数据
        all_comments = Comment.query.all()
        print(f"\n数据库中评论总数: {len(all_comments)}")

        for i, comment in enumerate(all_comments[:5]):  # 只显示前5个作为示例
            print(
                f"   评论 {i+1}: ID={comment.id}, post_id={comment.post_id}, video_id={comment.video_id}, news_id={comment.news_id}")


if __name__ == "__main__":
    test_post_detail_query()
