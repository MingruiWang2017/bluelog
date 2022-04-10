import unittest

from flask import url_for

from bluelog import create_app
from bluelog.extensions import db
from bluelog.models import Admin


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')  # 使用测试环境配置创建程序实例
        self.context = app.test_request_context()
        self.context.push()  # 显式推送请求上下文
        self.client = app.test_client()  # 测试客户端
        self.runner = app.test_cli_runner()  # 命令行测试运行器

        db.create_all()
        user = Admin(name='Jack', username='jack', about='I am test', blog_title='Testlog', blog_sub_title='a test')
        user.set_password('123456789')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()  # 显式关闭上下文

    def login(self, username=None, password=None):
        if username is None and password is None:
            username = 'jack'
            password = '123456789'

        return self.client.post(url_for('auth.login'), data=dict(
            username=username,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
