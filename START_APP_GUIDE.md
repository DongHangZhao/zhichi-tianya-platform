# 🚀 应用启动指南（已修复循环导入）

## ✅ 问题已修复

之前启动时报错 `ImportError: cannot import name 'app' from 'app'`，现在已经修复完成！

## 🔧 修复内容

**修改文件**：`scheduler.py`

**修改方式**：使用延迟导入策略，避免循环依赖

```python
# 修改前（错误）
from app import app, db

# 修改后（正确）
def get_app():
    """获取 app 实例"""
    from app import app
    return app
```

## 🎯 启动步骤

### 方法一：使用批处理文件（推荐）
```bash
start_server.bat
```

### 方法二：手动启动
```bash
python run.py
```

### 方法三：直接运行 app
```bash
python app.py
```

## ✨ 预期输出

成功启动后应该看到：

```
================================
   咫尺天涯社交平台启动器
================================

正在启动咫尺天涯社交平台...

 * Running on http://127.0.0.1:5000
定时任务线程已启动
定时任务已启动，将在每天 08:00 自动抓取新闻
Press CTRL+C to quit
```

## 🌐 访问地址

启动成功后，打开浏览器访问：

- **首页**: http://localhost:5000
- **新闻列表**: http://localhost:5000/news
- **新闻日历**: http://localhost:5000/news/calendar
- **视频**: http://localhost:5000/videos
- **论坛**: http://localhost:5000/forum

## 🔍 功能验证

### 1. 检查定时任务是否启动
查看控制台输出，应该有：
```
定时任务线程已启动
定时任务已启动，将在每天 08:00 自动抓取新闻
```

### 2. 测试新闻抓取
打开新终端，运行：
```bash
python test_news_scraper.py
```

### 3. 查看数据库
```bash
sqlite3 users.db
```
```sql
SELECT COUNT(*) FROM news;
SELECT source, COUNT(*) FROM news GROUP BY source;
```

## ⏰ 定时任务说明

### 默认配置
- **执行时间**：每天早上 8:00
- **执行频率**：每天一次
- **执行内容**：从多个新闻源抓取新闻并保存到数据库

### 修改执行时间
编辑 `scheduler.py`，找到这行：
```python
schedule.every().day.at("08:00").do(self.daily_news_fetch)
```

修改为其他时间，例如：
```python
# 早上 7 点
schedule.every().day.at("07:00").do(self.daily_news_fetch)

# 晚上 10 点
schedule.every().day.at("22:00").do(self.daily_news_fetch)
```

### 手动触发
如果需要立即执行一次新闻抓取：
```bash
python news_scraper.py
```

## 🛠️ 故障排除

### 问题 1：仍然报错循环导入
**症状**：还是显示 `ImportError: cannot import name 'app'`

**解决**：
1. 确认 `scheduler.py` 已经修改
2. 删除 `__pycache__` 文件夹
3. 重新启动应用

```bash
# Windows
rmdir /s /q __pycache__
start_server.bat

# Linux/Mac
rm -rf __pycache__
python run.py
```

### 问题 2：定时任务未启动
**症状**：控制台没有显示"定时任务线程已启动"

**解决**：
1. 检查 `app.py` 中是否有这两行：
   ```python
   from scheduler import init_scheduler
   init_scheduler()
   ```
2. 确认没有语法错误
3. 重启应用

### 问题 3：新闻抓取失败
**症状**：显示"抓取新华网失败：Connection timeout"

**解决**：
1. 检查网络连接
2. 确认能访问新华网等网站
3. 可能是临时网络问题，稍后重试
4. 增加超时时间（在 `news_scraper.py` 中修改 timeout 参数）

## 📊 监控日志

### 查看定时任务执行日志
定时任务每次执行都会输出日志：

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

### 查看数据库记录
```sql
-- 查看今天的新闻
SELECT * FROM news 
WHERE DATE(timestamp) = DATE('now');

-- 查看最新 10 条新闻
SELECT id, title, source, timestamp 
FROM news 
ORDER BY timestamp DESC 
LIMIT 10;
```

## 🎉 恭喜！

现在您的应用已经可以：

✅ 正常启动，无循环导入错误  
✅ 自动运行定时任务  
✅ 每天抓取真实新闻  
✅ 通过日历浏览新闻  
✅ 完整的数据持久化  

**一切就绪，开始使用吧！** 🚀
