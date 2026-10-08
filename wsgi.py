"""
WSGI 入口文件 —— 供 gunicorn / uWSGI / 云平台调用。

用法（生产）：
    gunicorn wsgi:app --bind 0.0.0.0:8000 --workers 1 --threads 4 --timeout 120

说明：由于 app.py 在导入时会启动后台线程（新闻定时抓取、在线状态清理）
且使用 SQLite，故生产环境使用「单 worker + 多线程」模式，避免任务重复执行。
"""
import os
from app import app  # noqa: F401  ——gunicorn 通过 `wsgi:app` 引用

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
