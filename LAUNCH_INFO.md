# 咫尺天涯社交平台 - 启动与开发说明

## 如何启动项目

### 方法一：使用批处理脚本（Windows）
双击运行 `start_server.bat` 或在命令行中执行：
```bash
start_server.bat
```

### 方法二：直接运行Python脚本
```bash
cd python_web_project
python run.py
```

> **说明**: start_server.bat 是一个Windows批处理脚本，它内部实际执行的就是 `python run.py` 命令，但提供了额外的环境检查和用户友好的提示信息。

### 3. 访问应用
打开浏览器访问：`http://localhost:5000`

## 默认账户信息
- 管理员账户：admin / password
- 示例用户：FallPetal 和 赵栋行001（已包含在数据库中）

## 开发工具脚本

### 初始化脚本
- `init_db.py` - 初始化数据库
- `initialize_data.py` - 初始化示例数据
- `initialize_builtin_users.py` - 初始化内置用户
- `initialize_user_status.py` - 初始化用户状态

### 管理脚本
- `list_users.py` - 列出所有用户
- `manage_news.py` - 管理新闻数据
- `simple_thumbnail_generator.py` - 生成缩略图

### 修复脚本
- `migrate_posts_table.py` - 修复帖子表结构

### 部署脚本
- `start_server.bat` - Windows启动脚本
- `deploy.bat` - Windows部署脚本
- `run_app.py` - 替代启动脚本

### 测试脚本
- `completion_report.py` - 生成完成报告

## 注意事项
- 项目使用SQLite数据库，数据存储在app.db文件中
- 首次启动会自动创建必要的数据库表
- 应用会在5000端口启动
- 所有开发工具脚本均已包含在项目目录中

## 功能概览
- 用户注册/登录系统
- 帖子、视频、新闻发布
- 用户间关注、点赞、评论、私信
- 热度排行功能
- 管理员后台管理