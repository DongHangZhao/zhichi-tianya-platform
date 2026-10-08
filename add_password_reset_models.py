'''
Author: your name
Date: 2026-04-29 15:12:35
LastEditTime: 2026-04-29 15:12:36
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\add_password_reset_models.py
'''
# -*- coding: utf-8 -*-
"""
添加密码重置相关数据库模型
"""

import os
import sys
from app import app, db
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def add_password_reset_models():
    """添加密码重置模型到models文件"""

    models_file = os.path.join(os.path.dirname(
        __file__), 'models', '__init__.py')

    # 读取现有内容
    with open(models_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否已经存在
    if 'class PasswordResetRequest' in content:
        print("密码重置模型已存在")
        return

    # 在文件末尾添加新模型
    new_models = '''


class PasswordResetRequest(db.Model):
    """密码重置请求模型"""
    __tablename__ = 'password_reset_requests'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    verification_code = db.Column(db.String(6), nullable=False)  # 6位验证码
    created_at = db.Column(FlexibleDateTime, default=datetime.now)
    expires_at = db.Column(FlexibleDateTime, nullable=False)  # 过期时间
    is_used = db.Column(db.Boolean, default=False)  # 是否已使用
    used_at = db.Column(FlexibleDateTime)  # 使用时间
    
    # 关系
    user = db.relationship('User', backref=db.backref('reset_requests', lazy=True))
    
    def is_valid(self):
        """检查验证码是否有效"""
        return not self.is_used and datetime.now() < self.expires_at
    
    def __repr__(self):
        return f'<PasswordResetRequest User:{self.user_id} Code:{self.verification_code}>'


class PasswordChangeLog(db.Model):
    """密码修改日志模型"""
    __tablename__ = 'password_change_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_by = db.Column(db.String(50))  # 'user', 'admin', 'system'
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(FlexibleDateTime, default=datetime.now)
    reason = db.Column(db.String(200))  # 修改原因
    
    # 关系
    user = db.relationship('User', backref=db.backref('password_logs', lazy=True))
    
    def __repr__(self):
        return f'<PasswordChangeLog User:{self.user_id} By:{self.changed_by}>'

'''

    # 追加到文件
    with open(models_file, 'a', encoding='utf-8') as f:
        f.write(new_models)

    print("已添加密码重置模型")


if __name__ == '__main__':
    with app.app_context():
        add_password_reset_models()
        db.create_all()
        print("数据库表已创建")
