'''
Author: your name
Date: 2026-04-29 15:19:34
LastEditTime: 2026-04-29 15:19:34
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\register_password_blueprint.py
'''
# -*- coding: utf-8 -*-
"""
注册密码管理蓝图到app.py
"""


import os
app_file = os.path.join(os.path.dirname(__file__), 'app.py')

# 读取文件
with open(app_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 检查是否已注册
if 'password_bp' in content:
    print("密码管理蓝图已注册")
    exit()

# 在 delete_bp 注册后添加密码管理蓝图
old_text = """# 注册删除功能蓝图
app.register_blueprint(delete_bp, url_prefix='/delete')

# 注册新闻路由蓝图
app.register_blueprint(news_bp, url_prefix='/news')"""

new_text = """# 注册删除功能蓝图
app.register_blueprint(delete_bp, url_prefix='/delete')

# 注册密码管理路由蓝图
from routes.password_routes import password_bp
app.register_blueprint(password_bp, url_prefix='/password')

# 注册新闻路由蓝图
app.register_blueprint(news_bp, url_prefix='/news')"""

content = content.replace(old_text, new_text)

# 写回文件
with open(app_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("已注册密码管理蓝图")
