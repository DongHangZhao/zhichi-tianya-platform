'''
Author: your name
Date: 2026-01-19 07:43:12
LastEditTime: 2026-01-19 07:43:12
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\test_news_features.py
'''
"""
测试新闻功能的各种特性
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import News, User
from scrape_news import update_daily_news
from datetime import datetime

def test_news_features():
    """
    测试新闻功能
    """
    print("开始测试新闻功能...")
    
    with app.app_context():
        # 检查新闻表是否存在
        try:
            news_count = News.query.count()
            print(f"✓ 新闻表存在，当前新闻数量: {news_count}")
        except Exception as e:
            print(f"✗ 新闻表不存在或访问出错: {e}")
            return False
        
        # 检查新闻字段是否完整
        try:
            sample_news = News.query.first()
            if sample_news:
                fields_to_check = ['title', 'content', 'summary', 'image_url', 'source', 'timestamp', 'views', 'likes_count']
                missing_fields = []
                for field in fields_to_check:
                    if not hasattr(sample_news, field):
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"✗ 缺少字段: {missing_fields}")
                else:
                    print("✓ 所有新闻字段存在")
                    print(f"  示例新闻标题: {sample_news.title[:50]}...")
                    print(f"  图片URL: {sample_news.image_url}")
                    print(f"  来源: {sample_news.source}")
                    print(f"  时间: {sample_news.timestamp}")
            else:
                print("? 没有找到示例新闻，尝试更新新闻数据")
                update_daily_news()
                news_count_after = News.query.count()
                print(f"更新后新闻数量: {news_count_after}")
        except Exception as e:
            print(f"✗ 检查新闻字段时出错: {e}")
            return False
        
        # 测试分页功能（通过模拟）
        try:
            # 模拟分页查询
            page_1 = News.query.order_by(News.timestamp.desc()).paginate(page=1, per_page=5, error_out=False)
            print(f"✓ 分页功能正常，第一页有 {len(page_1.items)} 条新闻")
        except Exception as e:
            print(f"✗ 分页功能异常: {e}")
            return False
        
        print("✓ 所有新闻功能测试通过！")
        return True

def test_search_functionality():
    """
    测试搜索功能
    """
    print("\n开始测试搜索功能...")
    
    with app.app_context():
        try:
            # 测试新闻搜索功能
            sample_news = News.query.first()
            if sample_news:
                search_keyword = sample_news.title.split()[0] if sample_news.title.split() else "新闻"
                
                # 模拟搜索
                search_results = News.query.filter(
                    db.or_(
                        News.title.contains(search_keyword),
                        News.content.contains(search_keyword),
                        News.source.contains(search_keyword)
                    )
                ).all()
                
                print(f"✓ 搜索功能正常，关键词 '{search_keyword}' 找到 {len(search_results)} 条结果")
            else:
                print("? 没有新闻数据用于搜索测试")
        except Exception as e:
            print(f"✗ 搜索功能异常: {e}")
            return False
    
    print("✓ 搜索功能测试通过！")
    return True

if __name__ == "__main__":
    print("="*50)
    print("新闻功能测试")
    print("="*50)
    
    success1 = test_news_features()
    success2 = test_search_functionality()
    
    print("\n" + "="*50)
    if success1 and success2:
        print("✓ 所有测试通过！新闻功能正常工作。")
    else:
        print("✗ 部分测试失败，请检查上述错误。")
    print("="*50)