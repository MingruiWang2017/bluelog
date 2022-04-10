from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from bluelog.extensions import db


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))  # 用户登录的用户名
    password_hash = db.Column(db.String(128))  # 保存密码的哈希，不保存明文
    blog_title = db.Column(db.String(60), comment="博客标题")
    blog_sub_title = db.Column(db.String(100), comment="博客副标题")
    name = db.Column(db.String(30), comment="用户昵称")
    about = db.Column(db.Text, comment="关于信息")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)  # 分类名称是不重复的
    # 关系属性posts，一对多
    posts = db.relationship('Post', back_populates='category')

    def delete(self):
        """自定义的分类删除方法，当一个分类被删除时，其所有的文章有改为default分类"""
        default_category = Category.query.get(1)
        posts = self.posts[:]
        for post in posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    slug = db.Column(db.String(512), comment="为标题生成ASCII-only slug")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    can_comment = db.Column(db.Boolean, default=True)

    # 外键：分类id
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    # 关联属性：分类多对一， 评论一对多
    category = db.relationship('Category', back_populates='posts')
    comments = db.relationship('Comment', back_populates='post', cascade='all, delete-orphan')


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30), comment="评论者")
    email = db.Column(db.String(254), comment="评论者邮箱")
    site = db.Column(db.String(255), comment="站点")
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False, comment="评论是否来自管理员")
    reviewed = db.Column(db.Boolean, default=False, comment="评论是否已被管理员审核")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 指向自己类的外键：回复评论与被回复的评论时多对一
    replied_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 外键：与post多对一
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    # 关系属性
    post = db.relationship('Post', back_populates='comments')
    # 评论的回复，和评论是多对一关系
    replies = db.relationship('Comment', back_populates='replied', cascade='all, delete-orphan')
    # 被回复的评论，和他的回复是一对多关系。
    # 将remote_side参数设为id字段，我们就把id字段定义为关系的远程侧（Remote Side），
    # 而replied_id就相应地变为本地侧（Local Side）。
    # replied_id是外键（定义在“多”一侧），则replied在“一”一侧，即remote_side远端（set remote_side on the many-to-one side）；
    # replies是集合关系属性（定义在“一”一侧）。
    # replied_id -> replied -> replies
    replied = db.relationship('Comment', back_populates='replies', remote_side=[id])


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
