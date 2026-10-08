'''
Author: your name
Date: 2026-03-15 01:34:48
LastEditTime: 2026-03-15 01:34:48
LastEditors: your name
Description: In User Settings Edit
FilePath: \Q文件\python_web_project\routes\delete.py
'''
"""
删除功能路由模块
包含视频、帖子、评论的删除功能
"""
from models import db, Video, Post, Comment, ContentHistory, VideoLike, PostLike
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user

delete_bp = Blueprint('delete', __name__)


@delete_bp.route('/delete_video/<int:video_id>', methods=['POST'])
@login_required
def delete_video(video_id):
    """删除视频"""
    video = Video.query.get_or_404(video_id)

    # 检查用户权限（必须是视频上传者或管理员）
    if video.uploader_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此视频', 'danger')
        return redirect(url_for('video_detail', video_id=video_id))

    # 创建删除记录
    history = ContentHistory(
        content_type='video',
        content_id=video.id,
        field_name='deleted',
        old_value=video.title,
        new_value='[已删除]',
        user_id=current_user.id
    )
    db.session.add(history)

    # 删除相关的点赞和评论
    VideoLike.query.filter_by(video_id=video_id).delete()
    Comment.query.filter_by(video_id=video_id).delete()

    # 删除视频记录
    db.session.delete(video)
    db.session.commit()

    flash('视频已删除', 'success')
    return redirect(url_for('videos'))


@delete_bp.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    """删除帖子"""
    post = Post.query.get_or_404(post_id)

    # 检查用户权限（必须是帖子作者或管理员）
    if post.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此帖子', 'danger')
        return redirect(url_for('post_detail', post_id=post_id))

    # 创建删除记录
    history = ContentHistory(
        content_type='post',
        content_id=post.id,
        field_name='deleted',
        old_value=post.title,
        new_value='[已删除]',
        user_id=current_user.id
    )
    db.session.add(history)

    # 删除相关的点赞和评论
    PostLike.query.filter_by(post_id=post_id).delete()
    Comment.query.filter_by(post_id=post_id).delete()

    # 删除帖子记录
    db.session.delete(post)
    db.session.commit()

    flash('帖子已删除', 'success')
    return redirect(url_for('forum'))


@delete_bp.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    """删除评论"""
    comment = Comment.query.get_or_404(comment_id)

    # 检查用户权限（必须是评论作者或管理员）
    if comment.author_id != current_user.id and not current_user.is_admin:
        flash('您没有权限删除此评论', 'danger')
        return redirect(url_for('index'))

    # 保存评论信息用于记录
    comment_content = comment.content[:50] if len(
        comment.content) > 50 else comment.content
    post_id = comment.post_id
    video_id = comment.video_id
    news_id = comment.news_id

    # 创建删除记录
    history = ContentHistory(
        content_type='comment',
        content_id=comment.id,
        field_name='deleted',
        old_value=comment_content,
        new_value='[已删除]',
        user_id=current_user.id
    )
    db.session.add(history)

    # 更新对应内容的评论数
    if post_id:
        post = Post.query.get(post_id)
        if post:
            post.comments_count = max(0, (post.comments_count or 0) - 1)
    elif video_id:
        video = Video.query.get(video_id)
        if video:
            video.comments_count = max(0, (video.comments_count or 0) - 1)
    elif news_id:
        news = News.query.get(news_id)
        if news:
            news.comments_count = max(0, (news.comments_count or 0) - 1)

    # 删除评论
    db.session.delete(comment)
    db.session.commit()

    flash('评论已删除', 'success')

    # 根据评论类型返回不同页面
    if post_id:
        return redirect(url_for('post_detail', post_id=post_id))
    elif video_id:
        return redirect(url_for('video_detail', video_id=video_id))
    elif news_id:
        return redirect(url_for('news_detail', news_id=news_id))
    else:
        return redirect(url_for('index'))
