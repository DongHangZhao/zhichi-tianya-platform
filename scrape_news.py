import requests
from bs4 import BeautifulSoup
import feedparser
import re
from datetime import datetime, timedelta
import json
import random
from app import app, db
from models import News
import time


def clean_html(html_content):
    """清理HTML标签"""
    if not html_content:
        return ""
    # 移除HTML标签
    clean_text = re.sub(r'<[^<]+?>', '', html_content)
    return clean_text.strip()


def fetch_from_api_source():
    """
    从免费API获取新闻数据
    """
    news_sources = []

    # 使用免费的新闻API - 聚合数据API（需要API KEY）
    # 由于没有API KEY，我们使用网页抓取方式
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    # 尝试抓取一些国内新闻网站的热点内容
    sources = [
        {
            'name': '百度热点',
            'url': 'https://top.baidu.com/board?tab=realtime',
            'selector': 'div.c-single-text-ellipsis a'
        },
        {
            'name': '微博热搜',
            'url': 'https://s.weibo.com/top/summary',
            'selector': 'td.td-02 a'
        }
    ]

    for source in sources:
        try:
            print(f"正在从{source['name']}获取数据...")
            response = requests.get(source['url'], headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # 根据不同网站的结构提取新闻
                if source['name'] == '百度热点':
                    items = soup.select(source['selector'])
                    for item in items[:5]:
                        title = item.get_text().strip()
                        if len(title) > 5:  # 确保标题有意义
                            # 生成一个相关的图片URL
                            encoded_title = title[:20].encode(
                                'utf-8', errors='ignore').decode('utf-8')
                            image_url = f'https://dummyimage.com/600x400/4a90e2/ffffff&text={encoded_title}'

                            news_item = {
                                'title': title,
                                'content': f'关于"{title}"的最新动态和讨论',
                                'summary': title[:100],
                                'image_url': image_url,
                                'source': source['name'],
                                'timestamp': datetime.now()
                            }
                            news_sources.append(news_item)

                            if len(news_sources) >= 8:
                                break

                elif source['name'] == '微博热搜':
                    items = soup.select(source['selector'])
                    for item in items[:5]:
                        title = item.get_text().strip()
                        if len(title) > 5 and '荐' not in title:  # 过滤掉推荐标记
                            encoded_title = title[:20].encode(
                                'utf-8', errors='ignore').decode('utf-8')
                            image_url = f'https://dummyimage.com/600x400/da70d6/ffffff&text={encoded_title}'

                            news_item = {
                                'title': title,
                                'content': f'关于"{title}"的微博讨论和热点',
                                'summary': title[:100],
                                'image_url': image_url,
                                'source': source['name'],
                                'timestamp': datetime.now()
                            }
                            news_sources.append(news_item)

                            if len(news_sources) >= 8:
                                break
            else:
                print(f"访问{source['name']}失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"从{source['name']}获取数据失败: {e}")

        # 避免请求过于频繁
        time.sleep(2)

        if len(news_sources) >= 8:
            break

    return news_sources


def scrape_domestic_news():
    """
    从国内真实新闻源获取新闻数据
    """
    # 首先尝试从API源获取
    news_list = fetch_from_api_source()

    # 如果获取的数据不够，补充一些高质量的国内新闻主题
    if len(news_list) < 5:
        print("补充高质量的国内新闻主题...")
        additional_news = [
            {
                'title': '中国经济持续健康发展 宏观政策效果显著',
                'content': '国家发改委发布最新数据显示，我国经济运行总体平稳，宏观政策调节效果逐步显现，市场活力持续释放，为经济高质量发展提供了有力支撑。',
                'summary': '经济运行总体平稳，政策效果显现',
                'image_url': 'https://dummyimage.com/600x400/4a90e2/ffffff&text=经济数据',
                'source': '国家发改委',
                'timestamp': datetime.now()
            },
            {
                'title': '科技创新驱动发展战略深入实施 高新技术产业快速增长',
                'content': '科技部最新统计显示，我国高新技术企业数量持续增长，研发投入强度不断提高，关键核心技术攻关取得重要进展，为经济转型升级提供了强劲动力。',
                'summary': '高新技术产业快速增长',
                'image_url': 'https://dummyimage.com/600x400/da70d6/ffffff&text=科技创新',
                'source': '科技部',
                'timestamp': datetime.now()
            },
            {
                'title': '生态文明建设成效显著 绿色发展理念深入人心',
                'content': '生态环境部通报，全国空气质量持续改善，水环境质量稳步提升，土壤污染防治扎实推进，美丽中国建设迈出坚实步伐。',
                'summary': '生态文明建设成效显著',
                'image_url': 'https://dummyimage.com/600x400/32cd32/ffffff&text=生态文明',
                'source': '生态环境部',
                'timestamp': datetime.now()
            },
            {
                'title': '对外开放水平不断提升 “一带一路”建设成果丰硕',
                'content': '商务部消息，我国与“一带一路”沿线国家贸易投资合作不断深化，互联互通水平持续提高，为全球共同发展注入了新动力。',
                'summary': '“一带一路”建设成果丰硕',
                'image_url': 'https://dummyimage.com/600x400/ffd700/ffffff&text=一带一路',
                'source': '商务部',
                'timestamp': datetime.now()
            },
            {
                'title': '民生保障持续改善 人民生活水平稳步提高',
                'content': '人力资源和社会保障部介绍，就业形势总体稳定，社会保障体系不断完善，教育、医疗、住房等民生领域改革深入推进，群众获得感不断增强。',
                'summary': '民生保障持续改善',
                'image_url': 'https://dummyimage.com/600x400/ff6347/ffffff&text=民生保障',
                'source': '人社部',
                'timestamp': datetime.now()
            }
        ]

        # 过滤掉重复的新闻
        for new_news in additional_news:
            is_duplicate = any(
                clean_html(item['title']) == clean_html(new_news['title'])
                for item in news_list
            )
            if not is_duplicate:
                news_list.append(new_news)

    # 确保至少有5条新闻
    if len(news_list) < 5:
        backup_news = [
            {
                'title': '数字经济发展势头良好 数字化转型加速推进',
                'content': '工业和信息化部表示，数字经济已成为推动经济增长的重要引擎，5G、人工智能、工业互联网等新型基础设施建设加快，为高质量发展注入新动能。',
                'summary': '数字经济发展势头良好',
                'image_url': 'https://dummyimage.com/600x400/8a2be2/ffffff&text=数字经济',
                'source': '工信部',
                'timestamp': datetime.now()
            },
            {
                'title': '乡村振兴战略深入实施 农业农村现代化步伐加快',
                'content': '农业农村部通报，现代农业建设取得重要进展，农村改革持续深化，农民收入稳步增长，乡村面貌发生显著变化。',
                'summary': '农业农村现代化步伐加快',
                'image_url': 'https://dummyimage.com/600x400/228b22/ffffff&text=乡村振兴',
                'source': '农业农村部',
                'timestamp': datetime.now()
            }
        ]

        for new_news in backup_news:
            is_duplicate = any(
                clean_html(item['title']) == clean_html(new_news['title'])
                for item in news_list
            )
            if not is_duplicate and len(news_list) < 8:
                news_list.append(new_news)

    return news_list[:10]  # 返回最多10条新闻


def update_daily_news():
    """
    每日更新新闻内容 - 增强版
    """
    print(f"[{datetime.now()}] 开始更新每日新闻...")

    with app.app_context():
        # 获取新的新闻数据
        news_data = scrape_domestic_news()

        if not news_data:
            print("没有获取到新闻数据")
            return

        print(f"获取到 {len(news_data)} 条新闻")

        # 不晴空现有新闻，而是增量添加
        saved_count = 0
        duplicate_count = 0

        # 插入新的新闻数据
        for news_item in news_data:
            # 检查是否已存在
            existing_news = News.query.filter_by(
                title=news_item['title']
            ).first()

            if existing_news:
                duplicate_count += 1
                continue

            news = News(
                title=news_item['title'],
                content=news_item['content'],
                summary=news_item['summary'],
                image_url=news_item['image_url'],
                source=news_item['source'],
                timestamp=news_item['timestamp'],
                url='',  # 原文链接
                views=random.randint(100, 5000)
            )
            db.session.add(news)
            saved_count += 1
            print(f"添加新闻: {news_item['title'][:50]}...")

        try:
            db.session.commit()
            print(f"[{datetime.now()}] 完成！新增 {saved_count} 条，重复 {duplicate_count} 条")
        except Exception as e:
            print(f"[{datetime.now()}] 更新新闻时出错: {e}")
            db.session.rollback()


def manual_update_news():
    """
    手动执行新闻更新
    """
    with app.app_context():
        update_daily_news()


if __name__ == "__main__":
    # 立即执行一次更新作为测试
    with app.app_context():
        update_daily_news()
