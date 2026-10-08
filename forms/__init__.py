from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FileField as WTFileField, PasswordField, HiddenField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms.widgets import TextArea
from werkzeug.security import check_password_hash


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = StringField('密码', validators=[DataRequired()])
    captcha = StringField('验证码', validators=[DataRequired(message='请输入验证码')])
    remember_me = BooleanField('记住我')
    submit = StringField('登录')

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        # 验证用户名和密码 - 延迟导入User模型以避免循环导入
        from models import User
        user = User.query.filter_by(username=self.username.data).first()
        if user is None or not user.check_password(self.password.data):
            self.password.errors = ['用户名或密码错误']
            return False

        # 设置user属性供登录使用
        self.user = user
        return True


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    avatar_choice = SelectField('选择头像', choices=[
        ('default_avatar.png', '默认头像'),
        ('uploads/avatars/avatar_1.png', '头像 1'),
        ('uploads/avatars/avatar_2.png', '头像 2'),
        ('uploads/avatars/avatar_3.png', '头像 3'),
        ('uploads/avatars/avatar_4.png', '头像 4'),
        ('uploads/avatars/avatar_5.png', '头像 5'),
        ('uploads/avatars/avatar_6.png', '头像 6'),
        ('uploads/avatars/avatar_7.png', '头像 7'),
        ('uploads/avatars/avatar_8.png', '头像 8'),
        ('uploads/avatars/avatar_9.png', '头像 9'),
        ('uploads/avatars/avatar_10.png', '头像 10')
    ], default='default_avatar.png')
    avatar_upload = FileField('或上传头像', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg', 'gif'], '只支持图片文件!')])
    captcha = StringField('验证码', validators=[DataRequired(message='请输入验证码')])
    captcha_hidden = HiddenField('验证码隐藏字段')
    submit = StringField('注册')

    def validate_username(self, username):
        from models import User  # 延迟导入以避免循环导入
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被使用。')

    def validate_email(self, email):
        from models import User  # 延迟导入以避免循环导入
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱已被使用。')

    def validate(self, extra_validators=None):
        # 调用父类验证方法
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False

        # 检查密码和确认密码是否一致
        if self.password.data != self.password2.data:
            self.password2.errors = ['密码和确认密码不匹配']
            return False

        return True


class ProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired()])
    bio = TextAreaField('个人简介')
    location = StringField('所在地区')
    website = StringField('个人网站')
    avatar = FileField('头像', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg', 'gif'], '只支持图片文件!')])
    submit = StringField('保存')

    def __init__(self, current_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_username = current_username

    def validate_username(self, username):
        from models import User  # 延迟导入以避免循环导入
        if username.data != self.current_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('用户名已被使用。')

    def validate_email(self, email):
        from models import User  # 延迟导入以避免循环导入
        user = User.query.filter_by(email=email.data).first()
        if user is not None and user.username != self.current_username:
            raise ValidationError('邮箱已被使用。')


class PostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    content = TextAreaField('内容', validators=[DataRequired()])
    image = FileField('配图', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], '只支持图片文件!')])
    video = FileField('视频', validators=[FileAllowed(
        ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm'], '只支持视频文件!')])
    submit = SubmitField('发布动态')


class EditPostForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    content = TextAreaField('内容', validators=[DataRequired()])
    image = FileField('配图', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], '只支持图片文件!')])
    video = FileField('视频', validators=[FileAllowed(
        ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm'], '只支持视频文件!')])
    submit = StringField('更新')


class VideoForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('描述')
    video_file = FileField('视频文件', validators=[FileAllowed(
        ['mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm'], '只支持视频文件!')])
    thumbnail = FileField(
        '缩略图', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '只支持图片文件!')])
    submit = SubmitField('上传')


class EditVideoForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('描述')
    thumbnail = FileField(
        '缩略图', validators=[FileAllowed(['jpg', 'png', 'jpeg'], '只支持图片文件!')])
    submit = SubmitField('更新')


class MessageForm(FlaskForm):
    content = TextAreaField(
        '消息内容', validators=[DataRequired(), Length(1, 500)])
    attachment = FileField('附件', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif', 'pdf', 'doc',
                           'docx', 'zip', 'rar', 'tar', 'gz', '7z', 'txt', 'mp4', 'avi', 'mov'], '只支持图片、文档、压缩包和视频文件!')])
    submit = SubmitField('发送')


class NewsForm(FlaskForm):
    title = StringField('标题', validators=[DataRequired(), Length(1, 200)])
    content = TextAreaField('内容', validators=[DataRequired()])
    image = FileField('配图', validators=[FileAllowed(
        ['jpg', 'png', 'jpeg'], '只支持图片文件!')])
    summary = StringField('摘要', validators=[Length(0, 500)])
    source = StringField('来源')
    submit = SubmitField('发布')


class AdminUserBanForm(FlaskForm):
    ban_type = SelectField('封禁类型', choices=[('full', '完全封禁'), ('post', '禁止发帖'), (
        'video', '禁止上传视频'), ('comment', '禁止评论')], validators=[DataRequired()])
    reason = TextAreaField('封禁原因', validators=[Length(0, 200)])
    submit = SubmitField('确认封禁')


class CommentForm(FlaskForm):
    content = TextAreaField(
        '评论内容', validators=[DataRequired(), Length(1, 1000)])
    submit = SubmitField('发布评论')
