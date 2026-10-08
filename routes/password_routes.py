'''
Author: your name
Date: 2026-04-29 15:34:53
LastEditTime: 2026-04-29 15:34:53
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\routes\password_routes_complete.py
'''
# -*- coding: utf-8 -*-
"""
密码管理路由 - 完整版
包括：修改密码、忘记密码（带验证码）、验证码重置、管理员重置密码
"""

from models import db
from models import User, PasswordResetRequest, PasswordChangeLog
import os
import sys
import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


password_bp = Blueprint('password', __name__)


def generate_verification_code():
    """生成6位验证码"""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])


@password_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """用户修改密码"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # 验证旧密码
        if not check_password_hash(current_user.password_hash, old_password):
            return jsonify({'success': False, 'message': '旧密码错误'}), 400

        # 验证新密码
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': '两次密码不一致'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

        # 更新密码
        current_user.password_hash = generate_password_hash(new_password)

        # 记录日志
        log = PasswordChangeLog(
            user_id=current_user.id,
            changed_by='user',
            ip_address=request.remote_addr,
            reason='用户主动修改'
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({'success': True, 'message': '密码修改成功，请重新登录'})

    return render_template('password/change_password.html')


@password_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码 - 提交重置请求（带图像验证码）"""
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email')
        captcha = request.form.get('captcha')

        # 验证图像验证码
        if 'captcha' not in session:
            return jsonify({'success': False, 'message': '验证码已失效，请刷新页面'}), 400

        if not captcha or captcha.upper() != session.get('captcha', '').upper():
            return jsonify({'success': False, 'message': '验证码错误'}), 400

        # 清除已使用的验证码
        session.pop('captcha', None)

        # 查找用户
        user = User.query.filter(
            (User.username == username_or_email) |
            (User.email == username_or_email)
        ).first()

        if not user:
            return jsonify({'success': False, 'message': '用户名或邮箱不存在'}), 404

        # 检查是否已有未过期的验证码
        existing_request = PasswordResetRequest.query.filter_by(
            user_id=user.id,
            is_used=False
        ).filter(
            PasswordResetRequest.expires_at > datetime.now()
        ).first()

        if existing_request:
            return jsonify({
                'success': False,
                'message': f'您已有待处理的请求，重置码为: {existing_request.verification_code}，请联系管理员获取'
            }), 400

        # 生成6位重置码
        verification_code = generate_verification_code()
        expires_at = datetime.now() + timedelta(minutes=30)  # 30分钟有效

        # 创建重置请求
        reset_request = PasswordResetRequest(
            user_id=user.id,
            verification_code=verification_code,
            expires_at=expires_at
        )
        db.session.add(reset_request)
        db.session.commit()

        # 返回重置码给用户（实际项目中应该发送给管理员）
        return jsonify({
            'success': True,
            'message': f'请求成功！您的重置码为: {verification_code}，请复制保存并联系管理员验证',
            'verification_code': verification_code
        })

    return render_template('password/forgot_password.html')


@password_bp.route('/verify-code', methods=['GET', 'POST'])
def verify_code():
    """验证重置码"""
    if request.method == 'POST':
        username = request.form.get('username')
        code = request.form.get('code')

        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 查找重置码
        reset_request = PasswordResetRequest.query.filter_by(
            user_id=user.id,
            verification_code=code,
            is_used=False
        ).filter(
            PasswordResetRequest.expires_at > datetime.now()
        ).first()

        if not reset_request:
            return jsonify({'success': False, 'message': '重置码无效或已过期'}), 400

        # 标记为已验证
        reset_request.is_used = True
        reset_request.used_at = datetime.now()
        db.session.commit()

        # 返回user_id用于重置密码
        return jsonify({
            'success': True,
            'message': '验证成功',
            'user_id': user.id
        })

    return render_template('password/verify_code.html')


@password_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """重置密码页面"""
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        if new_password != confirm_password:
            return jsonify({'success': False, 'message': '两次密码不一致'}), 400

        if len(new_password) < 6:
            return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

        # 更新密码
        user.password_hash = generate_password_hash(new_password)

        # 记录日志
        log = PasswordChangeLog(
            user_id=user.id,
            changed_by='system',
            ip_address=request.remote_addr,
            reason='忘记密码重置'
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({'success': True, 'message': '密码重置成功，请登录'})

    user_id = request.args.get('user_id')
    if not user_id:
        return redirect(url_for('password.verify_code'))

    return render_template('password/reset_password.html', user_id=user_id)


# 管理员功能
@password_bp.route('/admin/reset-user-password', methods=['POST'])
@login_required
def admin_reset_password():
    """管理员重置用户密码"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    if not new_password or len(new_password) < 6:
        return jsonify({'success': False, 'message': '密码长度不能少于6位'}), 400

    # 更新密码
    user.password_hash = generate_password_hash(new_password)

    # 记录日志
    log = PasswordChangeLog(
        user_id=user.id,
        changed_by='admin',
        ip_address=request.remote_addr,
        reason=f'管理员 {current_user.username} 重置密码'
    )
    db.session.add(log)

    db.session.commit()

    return jsonify({'success': True, 'message': f'已重置用户 {user.username} 的密码'})


@password_bp.route('/admin/view-reset-code', methods=['POST'])
@login_required
def admin_view_reset_code():
    """管理员查看用户的重置码"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': '无权操作'}), 403

    user_id = request.form.get('user_id')

    user = User.query.get(user_id)
    if not user:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    # 查找该用户的重置请求
    reset_request = PasswordResetRequest.query.filter_by(
        user_id=user.id,
        is_used=False
    ).filter(
        PasswordResetRequest.expires_at > datetime.now()
    ).order_by(PasswordResetRequest.created_at.desc()).first()

    if not reset_request:
        return jsonify({'success': False, 'message': '该用户没有有效的重置请求'}), 404

    return jsonify({
        'success': True,
        'message': f'用户 {user.username} 的重置码: {reset_request.verification_code}',
        'verification_code': reset_request.verification_code,
        'expires_at': reset_request.expires_at.strftime('%Y-%m-%d %H:%M:%S')
    })
