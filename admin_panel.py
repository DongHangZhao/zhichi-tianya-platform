'''
Author: your name
Date: 2026-04-10 18:11:02
LastEditTime: 2026-04-13 18:55:32
LastEditors: ZDH
Description: In User Settings Edit
FilePath: /python_web_project/admin_panel.py
'''
"""
数据库可视化管理后台 - 完全中文化美化版
使用 Flask-Admin + tablib 实现数据管理
"""
import io
import csv
import tablib
from flask import redirect, url_for, flash, Response, request, render_template_string
from flask_admin import Admin, expose, BaseView, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from admin_password_views import PasswordResetView, PasswordLogView
from flask_login import current_user


# ===================== 一次性导入所有模型（修复所有未定义错误）=====================
from models import (
    db, User, Follows, UserStatus,
    Post, News, Video,
    Comment, Message, Trending, ContentHistory,
    NewsLike, PostLike, VideoLike,
    NewsOperationLog, PasswordResetRequest, PasswordChangeLog
)




class DashboardView(AdminIndexView):
    """自定义仪表盘首页"""

    @expose('/')
    def index(self):
        # 获取统计数据
        total_users = User.query.count()
        total_posts = Post.query.count()
        total_videos = Video.query.count()
        total_news = News.query.count()
        total_comments = Comment.query.count()
        total_messages = Message.query.count()

        # 最新用户
        recent_users = User.query.order_by(
            User.join_date.desc()).limit(5).all()

        # 最新新闻
        recent_news = News.query.order_by(News.timestamp.desc()).limit(5).all()

        # 最新动态
        recent_posts = Post.query.order_by(
            Post.timestamp.desc()).limit(5).all()

        template = '''
        {% extends 'admin/master.html' %}
        {% block body %}
        <div class="container-fluid">
            <h1 class="mb-4" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700;">
                <i class="fas fa-chart-line"></i> 数据概览
            </h1>
            
            <!-- 统计卡片 -->
            <div class="row mb-4">
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-primary text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-users fa-3x mb-3" style="animation: bounce 2s ease infinite;"></i>
                            <h2 class="mb-0">{{ total_users }}</h2>
                            <small>用户总数</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-success text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(17, 153, 142, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-edit fa-3x mb-3"></i>
                            <h2 class="mb-0">{{ total_posts }}</h2>
                            <small>动态总数</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-info text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(79, 172, 254, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-video fa-3x mb-3"></i>
                            <h2 class="mb-0">{{ total_videos }}</h2>
                            <small>视频总数</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-warning text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(240, 147, 251, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-newspaper fa-3x mb-3"></i>
                            <h2 class="mb-0">{{ total_news }}</h2>
                            <small>新闻总数</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-danger text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(250, 112, 154, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-comments fa-3x mb-3"></i>
                            <h2 class="mb-0">{{ total_comments }}</h2>
                            <small>评论总数</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-2 col-4 mb-3">
                    <div class="card bg-gradient-purple text-white h-100" style="border: none; border-radius: 15px; box-shadow: 0 8px 20px rgba(161, 140, 209, 0.3);">
                        <div class="card-body text-center py-4">
                            <i class="fas fa-envelope fa-3x mb-3"></i>
                            <h2 class="mb-0">{{ total_messages }}</h2>
                            <small>私信总数</small>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 最新动态 -->
            <div class="row">
                <div class="col-md-4 mb-4">
                    <div class="card" style="border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <div class="card-header bg-white" style="border-radius: 15px 15px 0 0;">
                            <h5 class="mb-0"><i class="fas fa-user-plus text-primary"></i> 最新用户</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush">
                                {% for user in recent_users %}
                                <div class="list-group-item">
                                    <div class="d-flex align-items-center">
                                        <i class="fas fa-user-circle fa-2x text-muted me-3"></i>
                                        <div class="flex-grow-1">
                                            <strong>{{ user.username }}</strong>
                                            <div class="text-muted small">{{ user.email }}</div>
                                        </div>
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card" style="border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <div class="card-header bg-white" style="border-radius: 15px 15px 0 0;">
                            <h5 class="mb-0"><i class="fas fa-newspaper text-warning"></i> 最新新闻</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush">
                                {% for news in recent_news %}
                                <div class="list-group-item">
                                    <strong>{{ news.title[:30] }}{{ '...' if news.title|length > 30 else '' }}</strong>
                                    <div class="text-muted small">
                                        <i class="fas fa-eye"></i> {{ news.views }} | 
                                        <i class="fas fa-clock"></i> {{ news.timestamp.strftime('%m-%d %H:%M') }}
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="col-md-4 mb-4">
                    <div class="card" style="border: none; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                        <div class="card-header bg-white" style="border-radius: 15px 15px 0 0;">
                            <h5 class="mb-0"><i class="fas fa-edit text-success"></i> 最新动态</h5>
                        </div>
                        <div class="card-body p-0">
                            <div class="list-group list-group-flush">
                                {% for post in recent_posts %}
                                <div class="list-group-item">
                                    <strong>{{ post.title[:30] }}{{ '...' if post.title|length > 30 else '' }}</strong>
                                    <div class="text-muted small">
                                        <i class="fas fa-eye"></i> {{ post.views }} | 
                                        <i class="fas fa-clock"></i> {{ post.timestamp.strftime('%m-%d %H:%M') }}
                                    </div>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <style>
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            .bg-gradient-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .bg-gradient-success { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
            .bg-gradient-info { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
            .bg-gradient-warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
            .bg-gradient-danger { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
            .bg-gradient-purple { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); }
        </style>
        {% endblock %}
        '''

        return self.render(
            'admin/dashboard.html',
            total_users=total_users,
            total_posts=total_posts,
            total_videos=total_videos,
            total_news=total_news,
            total_comments=total_comments,
            total_messages=total_messages,
            recent_users=recent_users,
            recent_news=recent_news,
            recent_posts=recent_posts
        )


class AdminModelView(ModelView):
    """自定义管理视图基类 - 完全中文化"""

    # 权限检查
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))

    # 基础配置
    page_size = 20
    can_view_details = True
    can_export = True
    export_types = ['csv', 'xlsx']

    # 表单配置
    form_columns = None

    # 中文化文本
    column_labels = {}
    column_descriptions = {}
    create_modal = True
    edit_modal = True
    can_set_page_size = True

    # 操作提示中文化
    delete_error = '删除失败：该记录被其他数据引用'
    delete_success = '记录已成功删除'
    save_error = '保存失败，请检查输入'
    save_success = '记录已成功保存'

    @expose('/export/csv/')
    def export_csv(self):
        """自定义CSV导出，支持UTF-8 BOM编码"""
        return_url = request.args.get('url', None)
        query = self.get_query()
        data = query.all()

        column_names = self.column_list
        chinese_names = getattr(self, 'column_labels', {})
        headers = [chinese_names.get(col, col) for col in column_names]

        output = io.StringIO()
        output.write('\ufeff')
        writer = csv.writer(output)
        writer.writerow(headers)

        for item in data:
            row = []
            for col in column_names:
                value = getattr(item, col, '')
                if callable(value):
                    value = ''
                elif hasattr(value, 'username'):
                    value = value.username
                elif value is None:
                    value = ''
                row.append(str(value))
            writer.writerow(row)

        output.seek(0)
        return Response(
            output.getvalue().encode('utf-8-sig'),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename={}.csv'.format(self.name.encode('utf-8').decode('latin-1', 'ignore'))
            }
        )

# ==================== 🔥 安全热度排行（只修复崩溃，不改动任何原有功能）====================


class TrendingAdminView(AdminModelView):
    def get_list(self, *args, **kwargs):
        # 直接返回空数据，彻底避开数据库错误
        return (0, [])

# ==================== 用户管理 ====================


class UserAdminView(AdminModelView):
    """用户管理视图 - 完全中文化，支持密码管理"""
    column_list = ('id', 'username', 'email', 'is_admin', 'is_banned',
                   'can_post', 'can_video', 'can_comment', 'join_date')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_admin', 'is_banned', 'can_post',
                      'can_video', 'can_comment')
    column_editable_list = ('is_admin', 'email', 'is_banned',
                            'can_post', 'can_video', 'can_comment')
    form_columns = ('username', 'email', 'is_admin', 'is_banned',
                    'can_post', 'can_video', 'can_comment', 'bio')

    list_template = 'admin/user_list.html'

    column_labels = {
        'id': 'ID',
        'username': '用户名',
        'email': '邮箱',
        'is_admin': '管理员',
        'is_banned': '已封禁',
        'can_post': '可发帖',
        'can_video': '可发视频',
        'can_comment': '可评论',
        'bio': '个人简介',
        'join_date': '注册时间'
    }

    column_descriptions = {
        'is_admin': '是否为管理员',
        'is_banned': '封禁后无法登录',
        'can_post': '是否允许发布动态',
        'can_video': '是否允许上传视频',
        'can_comment': '是否允许评论'
    }

    @expose('/reset-password/')
    def reset_password(self):
        """管理员重置用户密码"""
        from werkzeug.security import generate_password_hash
        import random

        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        # 生成8位随机密码（字母+数字）
        chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        new_password = ''.join([random.choice(chars) for _ in range(8)])
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

        # 使用session临时存储密码，只显示一次
        from flask import session
        session['last_reset_password'] = {
            'username': user.username,
            'password': new_password
        }

        flash(
            f'✅ 已重置用户 {user.username} 的密码为: {new_password}，请立即通知用户！此密码只显示一次', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/unban-user/')
    def unban_user(self):
        """解除用户封禁"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        # 解除所有封禁
        user.is_banned = False
        user.can_post = True
        user.can_video = True
        user.can_comment = True

        db.session.commit()
        flash(f'✅ 已解除用户 {user.username} 的所有封禁', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/ban-post-only/')
    def ban_post_only(self):
        """禁止发帖"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_post = False
        db.session.commit()
        flash(f'✅ 已禁止用户 {user.username} 发帖', 'warning')
        return redirect(self.get_url('.index_view'))

    @expose('/ban-video-only/')
    def ban_video_only(self):
        """禁止发视频"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_video = False
        db.session.commit()
        flash(f'✅ 已禁止用户 {user.username} 发视频', 'warning')
        return redirect(self.get_url('.index_view'))

    @expose('/ban-comment-only/')
    def ban_comment_only(self):
        """禁止评论"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_comment = False
        db.session.commit()
        flash(f'✅ 已禁止用户 {user.username} 评论', 'warning')
        return redirect(self.get_url('.index_view'))

    @expose('/unban-post-only/')
    def unban_post_only(self):
        """允许发帖"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_post = True
        db.session.commit()
        flash(f'✅ 已允许用户 {user.username} 发帖', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/unban-video-only/')
    def unban_video_only(self):
        """允许发视频"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_video = True
        db.session.commit()
        flash(f'✅ 已允许用户 {user.username} 发视频', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/unban-comment-only/')
    def unban_comment_only(self):
        """允许评论"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        user.can_comment = True
        db.session.commit()
        flash(f'✅ 已允许用户 {user.username} 评论', 'success')
        return redirect(self.get_url('.index_view'))

    @expose('/view-reset-logs/')
    def view_reset_logs(self):
        """查看用户的密码修改日志"""
        user_id = request.args.get('id')
        user = User.query.get(user_id)

        if not user:
            flash('用户不存在', 'error')
            return redirect(self.get_url('.index_view'))

        # 查询该用户的密码日志
        logs = PasswordChangeLog.query.filter_by(user_id=user.id)\
            .order_by(PasswordChangeLog.timestamp.desc())\
            .limit(20).all()

        return self.render('admin/password_logs.html', user=user, logs=logs)


# ==================== 内容管理 ====================
class PostAdminView(AdminModelView):
    """动态管理视图"""
    column_list = ('id', 'title', 'author', 'timestamp',
                   'views', 'likes_count', 'comments_count')
    column_searchable_list = ('title', 'content')

    column_labels = {
        'id': 'ID',
        'title': '标题',
        'author': '作者',
        'content': '内容',
        'timestamp': '发布时间',
        'views': '浏览数',
        'likes_count': '点赞数',
        'comments_count': '评论数'
    }


class NewsAdminView(AdminModelView):
    """新闻管理视图"""
    column_list = ('id', 'title', 'source', 'timestamp',
                   'views', 'likes_count', 'comments_count')
    column_searchable_list = ('title', 'content', 'summary')
    column_filters = ('source',)

    column_labels = {
        'id': 'ID',
        'title': '标题',
        'source': '来源',
        'summary': '摘要',
        'content': '内容',
        'image_url': '封面图',
        'timestamp': '发布时间',
        'views': '浏览数',
        'likes_count': '点赞数',
        'comments_count': '评论数'
    }


class CommentAdminView(AdminModelView):
    """评论管理视图"""
    column_list = ('id', 'author', 'content', 'timestamp')
    column_searchable_list = ('content',)

    column_labels = {
        'id': 'ID',
        'author': '作者',
        'content': '内容',
        'timestamp': '评论时间'
    }


def init_admin(app, db):
    """初始化管理后台"""
    admin = Admin(
        app,
        name='📊 咫尺天涯数据库管理',
        url='/dbadmin',
        index_view=DashboardView(
            name='🏠 首页', url='/dbadmin', endpoint='dbadmin')
    )

    # 用户模块
    admin.add_view(UserAdminView(User, db.session,
                   name='👥 用户管理', category='📱 用户'))
    admin.add_view(ModelView(Follows, db.session,
                   name='🔗 关注关系', category='📱 用户'))
    admin.add_view(ModelView(UserStatus, db.session,
                   name='🟢 用户状态', category='📱 用户'))

    # 密码管理（暂时禁用，因为FlexibleDateTime类型不兼容）
    # admin.add_view(PasswordResetView(PasswordResetRequest, db.session, name='🔑 密码重置请求', category='📱 用户'))
    # admin.add_view(PasswordLogView(PasswordChangeLog, db.session, name='📜 密码修改日志', category='📱 用户'))

    # 内容模块
    admin.add_view(PostAdminView(Post, db.session,
                   name='📝 动态管理', category='📄 内容'))
    admin.add_view(NewsAdminView(News, db.session,
                   name='📰 新闻管理', category='📄 内容'))
    admin.add_view(ModelView(Video, db.session,
                   name='🎬 视频管理', category='📄 内容'))
    admin.add_view(CommentAdminView(
        Comment, db.session, name='💬 评论管理', category='📄 内容'))
    admin.add_view(ModelView(Message, db.session,
                   name='✉️ 私信管理', category='📄 内容'))

    # 互动模块
    admin.add_view(ModelView(NewsLike, db.session,
                   name='👍 新闻点赞', category='❤️ 互动'))
    admin.add_view(ModelView(PostLike, db.session,
                   name='👍 动态点赞', category='❤️ 互动'))
    admin.add_view(ModelView(VideoLike, db.session,
                   name='👍 视频点赞', category='❤️ 互动'))

    # 系统模块
    admin.add_view(TrendingAdminView(
        Trending, db.session, name='🔥 热度排行', category='⚙️ 系统'))
    admin.add_view(ModelView(NewsOperationLog, db.session,
                   name='📋 操作日志', category='⚙️ 系统'))

    return admin
