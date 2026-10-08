"""
项目配置文件（线上部署增强版）
定义应用程序的各种配置参数。

与原始 config.py 的差异（仅为支持云端部署，功能不变）：
1. DATABASE_URL 兼容 Render/Heroku 的 postgres:// 前缀（自动改写为 postgresql://）；
2. 仅在 SQLite 时才注入 check_same_thread 等专用参数，避免切到 PostgreSQL 时报错；
3. 上传体积上限由 1GB 下调为 200MB（云平台普遍限制）；
4. SECRET_KEY 默认值改为提示性文案，生产环境务必用环境变量覆盖。
"""

import os


def _normalize_db_url(url: str) -> str:
    """兼容部分云平台提供的 postgres:// 旧前缀。"""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-me-in-production'

    _db_url = _normalize_db_url(os.environ.get('DATABASE_URL', ''))
    SQLALCHEMY_DATABASE_URI = _db_url or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 按数据库类型选择引擎参数
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'check_same_thread': False,  # SQLite 特殊配置
                'detect_types': 3            # 启用类型检测
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_pre_ping': True,
            'pool_recycle': 280,
        }

    # 应用程序特定配置
    APP_NAME = '咫尺天涯 - 社交平台'
    VERSION = '1.0.0'
    AUTHOR = '赵栋行'

    # 文件上传配置
    MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB，适配云平台限制
    UPLOAD_FOLDER = 'static/uploads'

    # 分页配置
    ITEMS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
