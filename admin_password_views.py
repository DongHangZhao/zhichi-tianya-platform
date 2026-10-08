'''
Author: your name
Date: 2026-04-29 16:09:05
LastEditTime: 2026-04-29 16:09:05
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\admin_password_views.py
'''
# -*- coding: utf-8 -*-
"""
数据库管理后台密码管理视图
"""


from flask_admin.contrib.sqla import ModelView
class PasswordResetView(ModelView):
    """密码重置请求管理"""
    column_list = ('id', 'user', 'verification_code',
                   'created_at', 'expires_at', 'is_used', 'used_at')
    column_searchable_list = ('verification_code',)

    column_labels = {
        'id': 'ID',
        'user': '用户',
        'verification_code': '重置码',
        'created_at': '创建时间',
        'expires_at': '过期时间',
        'is_used': '已使用',
        'used_at': '使用时间'
    }

    form_columns = ('user', 'verification_code', 'expires_at', 'is_used')

    column_descriptions = {
        'is_used': '重置码只能使用一次',
        'expires_at': '重置码30分钟后过期'
    }


class PasswordLogView(ModelView):
    """密码修改日志管理"""
    column_list = ('id', 'user', 'changed_by',
                   'ip_address', 'timestamp', 'reason')
    column_searchable_list = ('reason', 'ip_address')

    column_labels = {
        'id': 'ID',
        'user': '用户',
        'changed_by': '修改者',
        'ip_address': 'IP地址',
        'timestamp': '时间',
        'reason': '原因'
    }

    column_descriptions = {
        'changed_by': 'user=用户自己, admin=管理员, system=系统',
        'reason': '密码修改的原因说明'
    }

    can_create = False
    can_edit = False
    can_delete = False
