"""
Gunicorn 生产配置。
用法：gunicorn -c gunicorn.conf.py wsgi:app
"""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# 单 worker + 多线程：兼容 app.py 中导入期启动的后台线程与 SQLite
workers = 1
threads = 4

timeout = 120
graceful_timeout = 30
keepalive = 5

accesslog = "-"
errorlog = "-"
loglevel = "info"
