<!--
 * @Author: your name
 * @Date: 2026-03-15 01:40:59
 * @LastEditTime: 2026-03-15 01:41:00
 * @LastEditors: ZDH
 * @Description: In User Settings Edit
 * @FilePath: \Q文件\python_web_project\DELETE_FEATURE_GUIDE.md
-->
# 删除功能实现指南

## 概述
已创建删除功能路由文件 `routes/delete.py`，包含视频、帖子、评论的完整删除功能。

## 已完成的工作

### 1. 创建删除路由文件
- 文件位置：`e:\办公练习\Html\Q文件\python_web_project\routes\delete.py`
- 包含三个删除路由：
  - `/delete_video/<int:video_id>` - 删除视频
  - `/delete_post/<int:post_id>` - 删除帖子
  - `/delete_comment/<int:comment_id>` - 删除评论

### 2. 删除功能特点
- ✅ 权限验证：只有作者或管理员可以删除
- ✅ 数据库记录：所有删除操作都会记录到 ContentHistory 表
- ✅ 级联删除：自动删除相关的点赞和评论
- ✅ 计数更新：自动更新父内容的评论计数
- ✅ 数据完整性：确保数据库一致性

## 需要手动完成的步骤

### 步骤 1: 在 app.py 中导入删除蓝图

打开 `app.py` 文件，在第 32 行（models 导入行）添加 ContentHistory：

```python
from models import db, User, Post, Video, Comment, Message, News, PostLike, VideoLike, NewsLike, Trending, Follows, UserStatus, ContentHistory
```

### 步骤 2: 注册删除蓝图

在 `app.py` 文件中找到 `db.init_app(app)` 这一行（约第 137 行），在它后面添加：

```python
# 初始化数据库
db.init_app(app)

# 注册删除功能蓝图
from routes.delete import delete_bp
app.register_blueprint(delete_bp, url_prefix='/delete')
```

### 步骤 3: 在模板中添加删除按钮

#### 3.1 视频详情页 (video_detail.html)
在编辑按钮旁边添加删除按钮：

```html
{% if current_user.id == video.uploader_id or current_user.is_admin %}
<a href="{{ url_for('edit_video', video_id=video.id) }}" class="btn btn-sm btn-outline-primary me-2">
    <i class="fas fa-edit"></i> 编辑
</a>
<form action="{{ url_for('delete.delete_video', video_id=video.id) }}" method="POST" style="display: inline;">
    <button type="submit" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定要删除这个视频吗？')">
        <i class="fas fa-trash"></i> 删除
    </button>
</form>
{% endif %}
```

#### 3.2 帖子详情页 (post_detail.html)
在编辑按钮旁边添加删除按钮：

```html
{% if current_user.id == post.author_id or current_user.is_admin %}
<a href="{{ url_for('edit_post', post_id=post.id) }}" class="btn btn-sm btn-outline-primary me-2">
    <i class="fas fa-edit"></i> 编辑
</a>
<form action="{{ url_for('delete.delete_post', post_id=post.id) }}" method="POST" style="display: inline;">
    <button type="submit" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定要删除这个帖子吗？')">
        <i class="fas fa-trash"></i> 删除
    </button>
</form>
{% endif %}
```

#### 3.3 评论区域（所有评论页面）
在每个评论旁边添加删除按钮：

```html
{% if comment.author_id == current_user.id or current_user.is_admin %}
<form action="{{ url_for('delete.delete_comment', comment_id=comment.id) }}" method="POST" style="display: inline;">
    <button type="submit" class="btn btn-sm btn-outline-danger" onclick="return confirm('确定要删除这条评论吗？')">
        <i class="fas fa-trash"></i> 删除
    </button>
</form>
{% endif %}
```

## 删除功能的数据库记录

所有删除操作都会在 `content_history` 表中创建记录：

```sql
-- 查看删除历史记录
SELECT * FROM content_history WHERE field_name = 'deleted';

-- 查看某个用户的删除历史
SELECT * FROM content_history WHERE user_id = [用户 ID] AND field_name = 'deleted';
```

## 测试删除功能

1. 启动应用
2. 登录一个账户
3. 发布视频/帖子/评论
4. 点击删除按钮
5. 确认删除
6. 检查：
   - 内容是否消失
   - 数据库中的 content_history 表是否有记录
   - 相关的点赞和评论是否被删除
   - 评论计数是否正确更新

## 注意事项

1. **权限控制**：只有内容作者或管理员可以删除
2. **二次确认**：删除前会弹出确认对话框
3. **数据备份**：删除记录会保存在 content_history 表中
4. **级联删除**：删除父内容会自动删除相关的子内容（点赞、评论）
5. **计数同步**：删除评论会自动更新父内容的评论计数

## 故障排除

如果删除功能不工作：
1. 检查是否正确导入了 ContentHistory 模型
2. 检查是否正确注册了蓝图
3. 检查浏览器控制台是否有 JavaScript 错误
4. 检查 Flask 日志是否有异常信息
