<!--
 * @Author: your name
 * @Date: 2026-03-15 02:14:40
 * @LastEditTime: 2026-03-15 02:14:40
 * @LastEditors: your name
 * @Description: In User Settings Edit
 * @FilePath: \Q文件\python_web_project\NEWS_SCRAPER_GUIDE.md
-->
# 新闻自动抓取与日历查看功能实现指南

## 📋 功能概述

本系统实现了以下功能：
1. **自动新闻抓取**：每天定时从多个国内新闻源抓取真实新闻（图文/视频）
2. **日历视图**：通过日历界面查看每天的新闻数据
3. **数据持久化**：所有抓取的新闻都保存到数据库
4. **多来源支持**：新华网、人民网、央视新闻、澎湃新闻等

## 🛠️ 技术栈扩展

### 新增依赖库
- **schedule**: 定时任务调度
- **requests**: HTTP 请求库，用于抓取网页
- **beautifulsoup4**: HTML 解析库，用于提取新闻数据

### 安装依赖
```bash
pip install -r requirements.txt
```

## 📁 新增文件说明

### 1. `news_scraper.py` - 新闻抓取器
负责从多个新闻源抓取新闻数据：
- 新华网
- 人民网
- 央视新闻（视频为主）
- 澎湃新闻

**主要功能**：
- `scrape_all()`: 抓取所有来源的新闻
- `get_news_detail()`: 获取新闻详情内容和图片
- `save_scraper_news()`: 保存新闻到数据库

### 2. `scheduler.py` - 定时任务管理器
负责每天自动执行新闻抓取任务：
- 默认每天早上 8:00 执行
- 后台线程运行，不影响主应用
- 可配置执行时间和频率

### 3. `routes/news.py` - 新闻路由模块
提供新闻相关的 API 端点：
- `/news/calendar`: 日历视图
- 支持按月浏览新闻

### 4. `templates/news_calendar.html` - 日历模板
美观的日历界面：
- 显示每天的新闻数量
- 点击日期可查看新闻列表
- 月份切换功能
- 统计信息展示

## ⚙️ 配置说明

### 1. 在 app.py 中注册蓝图
已自动完成：
```python
# 注册新闻路由蓝图
from routes.news import news_bp
app.register_blueprint(news_bp, url_prefix='/news')

# 初始化定时任务（新闻自动抓取）
from scheduler import init_scheduler
init_scheduler()
```

### 2. 定时任务配置
在 `scheduler.py` 中可以修改执行时间：
```python
# 每天早上 8 点执行
schedule.every().day.at("08:00").do(self.daily_news_fetch)

# 如果需要每 6 小时执行一次（测试用），取消注释：
# schedule.every(6).hours.do(self.daily_news_fetch)
```

## 🚀 使用方法

### 1. 启动应用
```bash
python app.py
```
应用启动后会自动：
- 启动定时任务调度器
- 准备在指定时间抓取新闻

### 2. 手动执行新闻抓取
```bash
python news_scraper.py
```
或在 Python 控制台中：
```python
from news_scraper import NewsScraper, save_scraper_news

scraper = NewsScraper()
news_list = scraper.scrape_all()
save_scraper_news(news_list)
```

### 3. 访问新闻页面
- **列表视图**: http://localhost:5000/news
- **日历视图**: http://localhost:5000/news/calendar

### 4. 日历操作
- 点击"上月"/"下月"切换月份
- 点击新闻标题查看详情
- 查看底部统计信息

## 📊 数据库结构

### News 表
| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | Integer | 主键 |
| title | String(200) | 新闻标题 |
| content | Text | 新闻内容 |
| summary | String(500) | 摘要 |
| source | String(50) | 来源（新华网/人民网等） |
| image_url | String(500) | 图片 URL |
| timestamp | DateTime | 抓取时间（本地时间） |

## 🔍 高级功能

### 1. 添加新的新闻源
在 `news_scraper.py` 中添加新的抓取方法：

```python
def fetch_custom_news(self):
    """抓取自定义新闻源"""
    news_list = []
    try:
        response = requests.get('目标 URL', headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 解析逻辑...
        news_items = soup.find_all('a', href=True)
        
        for item in news_items:
            title = item.get_text(strip=True)
            url = item['href']
            
            if title and len(title) > 5:
                news_list.append({
                    'title': title,
                    'source': '自定义来源',
                    'url': url,
                    'type': 'general'
                })
    except Exception as e:
        print(f"抓取失败：{e}")
    
    return news_list

# 在 scrape_all() 方法中调用
all_news.extend(self.fetch_custom_news())
```

### 2. 抓取视频新闻
系统已支持央视新闻视频抓取，会记录视频链接和标题。

### 3. 图片处理
如果新闻包含图片，会自动保存图片 URL 并显示在列表中。

## ⚠️ 注意事项

### 1. 网络爬虫礼仪
- 设置合理的超时时间（当前为 10 秒）
- 限制每次抓取的新闻数量（每个来源最多 10 条）
- 遵守 robots.txt 协议
- 不要频繁抓取，避免给服务器造成负担

### 2. 错误处理
- 单个来源抓取失败不会影响其他来源
- 所有异常都会被捕获并记录
- 建议在生产环境中添加日志记录

### 3. 数据去重
- 系统会自动检查标题是否重复
- 相同标题的新闻不会重复保存

### 4. 时区处理
- 所有时间使用本地时间（datetime.now()）
- 数据库存储和显示一致

## 📈 监控和维护

### 1. 查看抓取日志
控制台会输出：
```
[2026-03-15 08:00:00] 开始执行每日新闻抓取任务...
开始抓取新华网...
开始抓取人民网...
开始抓取央视新闻...
开始抓取澎湃新闻...
共抓取 35 条新闻
保存新闻：32 条，重复：3 条
[2026-03-15 08:00:15] 每日新闻抓取完成，保存 32 条新闻
```

### 2. 数据库查询
```sql
-- 查看今天的新闻
SELECT * FROM news 
WHERE DATE(timestamp) = DATE('now');

-- 查看某月的新闻总数
SELECT COUNT(*) FROM news 
WHERE strftime('%Y-%m', timestamp) = '2026-03';

-- 查看不同来源的新闻数量
SELECT source, COUNT(*) as count 
FROM news 
GROUP BY source;
```

### 3. 性能优化建议
- 定期清理旧新闻数据
- 为 timestamp 字段添加索引
- 考虑使用缓存减少数据库查询

## 🎯 未来扩展方向

### 1. 更多新闻源
- 地方新闻网站
- 行业垂直媒体
- 社交媒体热点

### 2. 智能分类
- 使用 NLP 技术自动分类新闻
- 关键词提取和标签生成
- 情感分析

### 3. 个性化推荐
- 根据用户浏览历史推荐新闻
- 热门新闻排行
- 相关新闻推荐

### 4. 多媒体支持
- 视频新闻在线播放
- 图片画廊
- 音频新闻

## ✅ 测试清单

- [ ] 依赖库安装成功
- [ ] 应用启动无错误
- [ ] 定时任务正常启动
- [ ] 手动执行新闻抓取成功
- [ ] 数据库中可以看到新闻数据
- [ ] 新闻列表页面正常显示
- [ ] 日历视图可以访问
- [ ] 月份切换功能正常
- [ ] 点击日期可以查看新闻
- [ ] 新闻详情页面正常

## 📝 故障排除

### 问题 1：抓取失败
**现象**：控制台显示抓取失败
**解决**：
- 检查网络连接
- 确认目标网站可访问
- 检查 User-Agent 是否被屏蔽
- 增加超时时间

### 问题 2：日历视图空白
**现象**：日历显示但没有新闻
**解决**：
- 确认数据库中有新闻数据
- 检查日期范围是否正确
- 查看浏览器控制台是否有错误

### 问题 3：定时任务未执行
**现象**：到了时间没有自动抓取
**解决**：
- 确认应用一直在运行
- 检查 scheduler 是否成功启动
- 查看控制台日志

### 问题 4：图片无法显示
**现象**：新闻图片加载失败
**解决**：
- 检查 image_url 是否有效
- 确认 static/uploads 目录存在
- 添加图片加载失败的占位图

## 🌟 总结

现在您的新闻系统具备：
✅ 自动抓取真实新闻（每天更新）
✅ 多个权威新闻来源
✅ 日历视图浏览
✅ 数据持久化存储
✅ 定时任务自动执行
✅ 完整的错误处理

所有新闻都是真实的、每天更新的，并且保存在数据库中供随时查看！
