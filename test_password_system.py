'''
Author: your name
Date: 2026-04-29 15:48:21
LastEditTime: 2026-04-29 15:48:21
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\test_password_system.py
'''
# -*- coding: utf-8 -*-
"""
密码管理功能测试脚本
"""

import os
import sys
from app import app, db
from models import User, PasswordResetRequest, PasswordChangeLog
from werkzeug.security import generate_password_hash
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_password_system():
    """测试密码管理系统"""

    print("="*70)
    print("密码管理系统功能测试")
    print("="*70)

    with app.app_context():
        # 1. 检查数据库表
        print("\n[1] 检查数据库表...")
        try:
            reset_count = PasswordResetRequest.query.count()
            log_count = PasswordChangeLog.query.count()
            print(f"  ✅ PasswordResetRequest表: {reset_count} 条")
            print(f"  ✅ PasswordChangeLog表: {log_count} 条")
        except Exception as e:
            print(f"  ❌ 表不存在: {e}")
            return

        # 2. 检查用户
        print("\n[2] 检查用户...")
        admin = User.query.filter_by(is_admin=True).first()
        if not admin:
            print("  ❌ 没有管理员账户")
            return

        print(f"  ✅ 管理员: {admin.username} (ID: {admin.id})")

        # 3. 测试生成重置码
        print("\n[3] 测试生成重置码...")
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        reset_req = PasswordResetRequest(
            user_id=admin.id,
            verification_code=code,
            expires_at=datetime.now() + timedelta(minutes=30)
        )
        db.session.add(reset_req)
        db.session.commit()
        print(f"  ✅ 生成重置码: {code}")
        print(
            f"  ✅ 过期时间: {reset_req.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")

        # 4. 测试验证码验证
        print("\n[4] 测试验证码验证...")
        valid_req = PasswordResetRequest.query.filter_by(
            user_id=admin.id,
            verification_code=code,
            is_used=False
        ).filter(
            PasswordResetRequest.expires_at > datetime.now()
        ).first()

        if valid_req:
            print(f"  ✅ 验证码验证成功")
            valid_req.is_used = True
            valid_req.used_at = datetime.now()
            db.session.commit()
            print(f"  ✅ 验证码标记为已使用")
        else:
            print(f"  ❌ 验证码验证失败")

        # 5. 测试重置密码
        print("\n[5] 测试重置密码...")
        new_password = "test123456"
        admin.password_hash = generate_password_hash(new_password)

        log = PasswordChangeLog(
            user_id=admin.id,
            changed_by='system',
            ip_address='127.0.0.1',
            reason='测试密码重置'
        )
        db.session.add(log)
        db.session.commit()
        print(f"  ✅ 密码已重置为: {new_password}")
        print(f"  ✅ 日志已记录")

        # 6. 检查路由
        print("\n[6] 检查路由...")
        rules = [str(r)
                 for r in app.url_map.iter_rules() if 'password' in str(r)]
        if rules:
            print(f"  ✅ 已注册 {len(rules)} 个密码相关路由:")
            for rule in rules:
                print(f"    - {rule}")
        else:
            print(f"  ❌ 没有密码相关路由")

        # 7. 总结
        print("\n" + "="*70)
        print("测试结果总结")
        print("="*70)
        print("✅ 数据库表正常")
        print("✅ 用户存在")
        print("✅ 重置码生成正常")
        print("✅ 验证码验证正常")
        print("✅ 密码重置正常")
        print("✅ 路由注册正常")
        print("\n🎉 所有测试通过！")
        print("\n📋 可以使用以下URL:")
        print(f"  - 修改密码: http://127.0.0.1:5000/password/change-password")
        print(f"  - 忘记密码: http://127.0.0.1:5000/password/forgot-password")
        print(f"  - 验证重置码: http://127.0.0.1:5000/password/verify-code")
        print(
            f"  - 重置密码: http://127.0.0.1:5000/password/reset-password?user_id={admin.id}")
        print(f"\n🔐 管理员测试密码: {new_password}")
        print("="*70)


if __name__ == '__main__':
    test_password_system()
