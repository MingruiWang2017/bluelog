import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog import db
from bluelog.utils import slugify
from bluelog.models import Admin, Category, Post, Comment, Link

fake = Faker()


def fake_admin():
    admin = Admin(
        username='admin',
        blog_title='Bluelog',
        blog_sub_title="No, I'm the real thing.",
        name='Jack Smith',
        about='Um, Jack, had a fun time as a member of CHAM... '
    )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)

    while count > 0:
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
            count -= 1
        except IntegrityError:
            # 当出现重复的分类字段时，回滚
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        title = fake.sentence()
        post = Post(
            title=title,
            body=fake.text(2000),
            slug=slugify(title),
            category=Category.query.get(random.randint(1, Category.query.count())),  # 随机获取一个分类
            timestamp=fake.date_time_this_year()
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    # 加盐10%为审核的评论，10%管理员评论
    salt = int(count * 0.1)

    for i in range(salt):
        # 未审核评论
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

        # 管理员评论
        comment = Comment(
            author='Jack Smith',
            email='jack@example.com',
            site='example.com',
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)

    db.session.commit()

    # 评论回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    twitter = Link(name='Twitter', url='#')
    facebook = Link(name='Facebook', url='#')
    linkedin = Link(name='Linkedin', url='#')
    github = Link(name='Github', url='#')
    db.session.add_all([twitter, facebook, linkedin, github])
    db.session.commit()
