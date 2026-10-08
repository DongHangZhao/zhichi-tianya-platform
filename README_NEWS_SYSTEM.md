<!--
 * @Author: your name
 * @Date: 2026-03-15 02:15:48
 * @LastEditTime: 2026-03-15 02:15:48
 * @LastEditors: your name
 * @Description: In User Settings Edit
 * @FilePath: \Q文件\python_web_project\README_NEWS_SYSTEM.md
-->
# 新闻自动抓取与日历系统 - 完整实现总结

## ✅ 已完成的功能

### 🎯 核心功能
1. **自动新闻抓取系统**
   - ✅ 从多个真实新闻源抓取（新华网、人民网、央视新闻、澎湃新闻）
   - ✅ 支持图文和视频新闻
   - ✅ 每天自动执行（默认早上 8 点）
   - ✅ 数据去重，避免重复保存

2. **日历视图系统**
   - ✅ 美观的日历界面展示新闻
   - ✅ 按日期分组显示
   - ✅ 月份切换功能
   - ✅ 统计信息展示
   - ✅ 点击日期查看具体新闻

3. **数据持久化**
   - ✅ 所有新闻保存到数据库
   - ✅ 记录来源、标题、内容、图片等
   - ✅ 时间戳使用本地时间
   - ✅ 完整的增删改查支持

### 📁 创建的新文件

#### 1. `news_scraper.py` (274 行)
新闻抓取器核心模块：
- `NewsScraper` 类：管理所有抓取逻辑
- 5 个抓取方法（新华网、人民网、央视、澎湃）
- 详情提取功能
- 数据保存功能

#### 2. `scheduler.py` (84 行)
定时任务管理器：
- 每日自动执行抓取
- 后台线程运行
- 可配置执行时间

#### 3. `routes/news.py` (50 行)
新闻路由蓝图：
- `/news/calendar` 日历视图路由
- 按月查询和分组

#### 4. `templates/news_calendar.html` (167 行)
日历模板：
- 响应式设计
- 直观的日期导航
- 新闻列表展示
- 统计面板

#### 5. `test_news_scraper.py` (74 行)
测试脚本：
- 快速验证抓取功能
- 数据库保存测试

#### 6. `NEWS_SCRAPER_GUIDE.md` (301 行)
完整使用指南：
- 安装说明
- 配置方法
- 故障排除
- 扩展指南

### 🔧 修改的文件

#### 1. `app.py`
```python
# 注册新闻路由蓝图
from routes.news import news_bp
app.register_blueprint(news_bp, url_prefix='/news')

# 初始化定时任务（新闻自动抓取）
from scheduler import init_scheduler
init_scheduler()
```

#### 2. `requirements.txt`
添加新依赖：
```
schedule==1.2.0      # 定时任务
requests==2.31.0     # HTTP 请求
beautifulsoup4==4.12.2  # HTML 解析
```

#### 3. `templates/news.html`
更新日历链接：
```html
<a href="{{ url_for('news_routes.news_calendar') }}" class="btn btn-outline-primary">
  <i class="fas fa-calendar-alt"></i> 日历查看
</a>
```

## 🚀 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python app.py
```
应用会自动：
- 启动定时任务
- 准备在每天早上 8 点抓取新闻

### 3. 手动测试抓取
```bash
python test_news_scraper.py
```

### 4. 访问页面
- **新闻列表**: http://localhost:5000/news
- **日历视图**: http://localhost:5000/news/calendar

## 📊 数据来源

### 支持的新闻源
1. **新华网** - 权威时政新闻
2. **人民网** - 综合新闻报道
3. **央视新闻** - 视频新闻为主
4. **澎湃新闻** - 深度报道

### 抓取内容
- ✅ 新闻标题
- ✅ 新闻内容（自动提取正文）
- ✅ 新闻图片（自动提取第一张图）
- ✅ 来源标识
- ✅ 发布时间（本地时间）
- ✅ 原文链接

## 🎨 界面展示

### 日历视图功能
- 📅 **月历展示**：完整的月份日历
- 📰 **新闻标记**：有新闻的日期高亮显示
- 🔢 **数量统计**：显示每天的新闻条数
- 📊 **月度统计**：总数、来源分布
- ⬅️➡️ **月份切换**：上月/下月导航
- 🔗 **快速访问**：点击新闻标题查看详情

### 新闻列表功能
- 🖼️ **图文展示**：带图片的新闻卡片
- 📝 **摘要预览**：显示前 100 字
- 🏷️ **来源标注**：清晰标识新闻来源
- ⏰ **时间显示**：本地时间格式化
- 🔍 **分页浏览**：每页 10 条新闻

## 💾 数据库设计

### News 表结构
```sql
CREATE TABLE news (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    summary VARCHAR(500),
    source VARCHAR(50),
    image_url VARCHAR(500),
    timestamp DATETIME,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0
);
```

### 索引优化建议
```sql
-- 为时间字段添加索引（提高日历查询速度）
CREATE INDEX idx_news_timestamp ON news(timestamp);

-- 为来源字段添加索引（提高统计查询速度）
CREATE INDEX idx_news_source ON news(source);
```

## 🔍 SQL 查询示例

### 查看今日新闻
```sql
SELECT * FROM news 
WHERE DATE(timestamp) = DATE('now');
```

### 按月统计
```sql
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as count
FROM news
WHERE strftime('%Y-%m', timestamp) = '2026-03'
GROUP BY DATE(timestamp)
ORDER BY date;
```

### 来源分布
```sql
SELECT 
    source,
    COUNT(*) as count
FROM news
GROUP BY source
ORDER BY count DESC;
```

## ⚙️ 高级配置

### 1. 修改抓取时间
编辑 `scheduler.py`:
```python
# 改为每天早上 6 点执行
schedule.every().day.at("06:00").do(self.daily_news_fetch)
```

### 2. 增加抓取频率
```python
# 每 6 小时执行一次
schedule.every(6).hours.do(self.daily_news_fetch)
```

### 3. 添加新新闻源
在 `news_scraper.py` 中添加：
```python
def fetch_custom_news(self):
    """自定义新闻源"""
    news_list = []
    try:
        response = requests.get('URL', headers=self.headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        # 解析逻辑...
    except Exception as e:
        print(f"抓取失败：{e}")
    return news_list
```

## ⚠️ 注意事项

### 1. 网络爬虫礼仪
- ✅ 设置合理的超时（10 秒）
- ✅ 限制抓取数量（每源 10 条）
- ✅ 遵守 robots.txt
- ✅ 不频繁抓取

### 2. 错误处理
- 单个来源失败不影响其他
- 所有异常都被捕获
- 建议添加日志记录

### 3. 数据维护
- 定期清理旧数据
- 监控数据库大小
- 备份重要数据

## 📈 性能优化

### 1. 数据库优化
```python
# 为 News 模型添加索引
class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)  # 添加索引
    source = db.Column(db.String(50), index=True)   # 添加索引
```

### 2. 缓存策略
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/news/calendar')
@cache.cached(timeout=300)  # 缓存 5 分钟
def news_calendar():
    # ...
```

### 3. 异步抓取
```python
import asyncio
import aiohttp

async def fetch_all_sources():
    """异步并发抓取所有来源"""
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_xinhua(session),
            fetch_people(session),
            fetch_cctv(session),
            fetch_thepaper(session)
        ]
        results = await asyncio.gather(*tasks)
    return results
```

## 🎯 未来扩展

### 短期目标
- [ ] 添加更多国内新闻源
- [ ] 实现新闻分类标签
- [ ] 关键词搜索功能
- [ ] 热门新闻排行

### 中期目标
- [ ] NLP 自动分类
- [ ] 情感分析
- [ ] 个性化推荐
- [ ] 新闻摘要生成

### 长期目标
- [ ] 实时新闻推送
- [ ] 多媒体新闻播放
- [ ] 用户评论系统
- [ ] 社交分享功能

## ✅ 测试清单

- [x] 依赖库安装成功
- [x] 应用启动无错误
- [x] 定时任务正常启动
- [x] 新闻抓取功能正常
- [x] 数据库保存成功
- [x] 日历视图可以访问
- [x] 月份切换功能正常
- [x] 新闻详情显示正常

## 📞 技术支持

如有问题，请检查：
1. 控制台日志输出
2. 数据库连接状态
3. 网络连接是否正常
4. 依赖库版本兼容性

## 🌟 总结

现在您的新闻系统完全实现了：

✅ **真实性**：所有新闻都是从真实网站抓取
✅ **自动化**：每天定时更新，无需手动操作
✅ **可视化**：美观的日历界面浏览
✅ **持久化**：完整保存到数据库
✅ **可扩展**：易于添加新的新闻源
✅ **实用性**：真实可用的生产级代码

所有功能都已就绪，可以直接使用！🎉
