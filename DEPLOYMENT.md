<!--
 * @Author: your name
 * @Date: 2026-01-10 13:04:44
 * @LastEditTime: 2026-01-10 13:04:44
 * @LastEditors: your name
 * @Description: In User Settings Edit
 * @FilePath: \Q文件\python_web_project\DEPLOYMENT.md
-->
# Python Web项目部署指南

## 项目概述

这是一个现代化的Python Web应用程序，使用Flask框架构建，具有响应式设计和完整的用户管理系统。

## 部署方式

### 方式一：使用部署脚本（推荐）

对于Windows用户，可以直接运行部署脚本：

```
双击 deploy.bat 文件
```

### 方式二：手动部署

1. 安装Python依赖：
   ```
   pip install -r requirements.txt
   ```

2. 启动应用：
   ```
   python app.py
   ```

3. 访问应用：
   打开浏览器并访问 `http://localhost:5000`

## 项目结构

```
python_web_project/
│
├── app.py                 # 主应用文件
├── config.py              # 配置文件
├── requirements.txt       # 项目依赖
├── README.md             # 项目说明
├── DEPLOYMENT.md         # 部署说明
├── run.py                # 启动脚本
├── test_app.py           # 测试文件
├── deploy.bat            # Windows部署脚本
├── static/               # 静态资源
│   ├── css/              # CSS样式文件
│   │   └── style.css
│   ├── js/               # JavaScript文件
│   │   └── main.js
│   └── images/           # 图片资源
│
├── templates/            # HTML模板
│   ├── base.html         # 基础模板
│   ├── index.html        # 首页
│   ├── users.html        # 用户管理页面
│   └── about.html        # 关于页面
│
└── database/             # 数据库文件
    └── users.db          # SQLite数据库（运行后自动生成）
```

## 功能说明

1. **首页** - 展示项目概览和特色功能
2. **用户管理** - 添加和查看用户信息
3. **关于我们** - 项目介绍

## 技术特性

- 基于Flask的后端框架
- SQLite数据库集成
- Bootstrap 5响应式设计
- RESTful API接口
- 前后端分离架构
- 移动端友好界面

## 生产环境部署建议

在生产环境中，建议：

1. 使用WSGI服务器（如Gunicorn或uWSGI）
2. 使用Nginx作为反向代理
3. 配置HTTPS
4. 设置适当的防火墙规则
5. 定期备份数据库

## 故障排除

如果遇到问题：

1. 确保Python 3.7+已安装
2. 检查端口5000是否被占用
3. 确认依赖包已正确安装
4. 查看控制台错误信息

## 维护者

- 赵栋行 (学号: 23105010330)
- 指导教师: 杨风涛、马金慧