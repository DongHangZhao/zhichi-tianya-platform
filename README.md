# 咫尺天涯 · 社交平台

> 一个基于 **Python Flask** 的综合社交平台 —— 集新闻资讯、短视频、图文动态、私信聊天于一体。
> “咫尺天涯”寓意：人与人虽可能相隔万里，通过网络仍能实现心灵的贴近交流。

<p align="left">
  <img alt="python" src="https://img.shields.io/badge/Python-3.11-blue">
  <img alt="flask" src="https://img.shields.io/badge/Flask-2.3-green">
  <img alt="license" src="https://img.shields.io/badge/License-MIT-yellow">
</p>

## ✨ 功能特性

| 模块 | 能力 |
|------|------|
| 👤 用户系统 | 注册 / 登录 / 注销、图形验证码、头像与资料管理、关注/粉丝、密码找回与重置 |
| 📝 内容发布 | 图文动态与短视频发布/编辑/删除、配图上传、内容修改历史追踪 |
| 💬 社交互动 | 点赞（帖/视频/新闻）、多态评论、私信聊天（支持附件）、实时在线状态（SSE 推送） |
| 📰 新闻资讯 | 真实新闻抓取（新华网/央视/澎湃）、日历视图、按日期/关键字/来源搜索、行为审计日志 |
| 🔥 热度排行 | 日/周/月排行，基于点赞·评论·浏览加权 + 时间衰减算法 |
| 🛡️ 管理后台 | Flask-Admin 数据后台、用户封禁（分级：发帖/视频/评论）、内容审核、密码重置 |

## 🧱 技术栈

- **后端**：Flask 2.3 · Flask-SQLAlchemy · Flask-Login · Flask-WTF · Flask-Admin
- **数据库**：SQLite（本地）/ PostgreSQL（线上，可通过 `DATABASE_URL` 切换）
- **前端**：Jinja2 · Bootstrap 5 · 原生 JavaScript（Fetch/AJAX 无刷新）
- **任务调度**：schedule + threading（每日 08:00 自动抓取新闻）
- **其他**：Pillow（头像压缩/验证码）、BeautifulSoup4（爬虫）

## 📁 项目结构

```
.
├── app.py                 # 主应用（路由 + 业务逻辑 + 模板过滤器）
├── admin_panel.py         # Flask-Admin 后台
├── config.py              # 配置（支持环境变量）
├── wsgi.py                # 生产 WSGI 入口
├── scheduler.py           # 定时任务（新闻抓取）
├── chinese_time_utils.py  # 中文时间格式化 / 热度算法
├── news_scraper_v2.py     # 新闻爬虫
├── models/                # 数据模型（16 张表）
├── forms/                 # Flask-WTF 表单
├── routes/                # 蓝图（news / delete / password）
├── utils/                 # 工具函数（图片、验证码、热度）
├── templates/             # Jinja2 模板
├── static/                # css / js / images / uploads
├── requirements.txt
├── Procfile / render.yaml / Dockerfile   # 部署配置
└── runtime.txt / .env.example
```

## 🚀 本地运行

```bash
# 1. 创建虚拟环境
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python run.py
# 或：python app.py

# 4. 浏览器访问
#    http://localhost:5000
```

> 首次启动会自动创建 SQLite 数据库（`app.db`）并建表。

## ☁️ 部署上线

本项目已内置多种部署配置，详见 **[部署指南.md](部署指南.md)**：

| 平台 | 特点 | 配置 |
|------|------|------|
| **PythonAnywhere** | 免费、文件持久化，SQLite 直接可用（**最省事**） | 手动配置 WSGI |
| **Render** | 连 GitHub 自动部署，免费版可配 PostgreSQL | `render.yaml` |
| **Docker / 自有服务器** | 完全可控 | `Dockerfile` + gunicorn |

**环境变量**（生产必填）：

```bash
FLASK_ENV=production
SECRET_KEY=<随机 64 位十六进制字符串>
DATABASE_URL=<可选，PostgreSQL 连接串；不填则用 SQLite>
```

## 👨‍🎓 作者信息

- **姓名**：赵栋行
- **学号**：23105010330
- **指导教师**：杨风涛、马金慧
- **学院**：信息工程学院 · 唐山工业职业技术大学
- **类型**：毕业设计 / Python Web 方向

## 📄 许可

本项目基于 [MIT License](LICENSE) 开源，仅供学习交流。
