import os
import sys


# 项目根目录绝对路径
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


# SQlite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, 'data.db')

MAIL_SERVER = os.getenv('MAIL_SERVER')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_SSL = True
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_AUTH_CODE')
MAIL_DEFAULT_SENDER = ('Bulelog Admin', MAIL_USERNAME)

BLUELOG_EMAIL = os.getenv('BLUELOG_EMAIL')
BLUELOG_POST_PER_PAGE = 10  # 每页显示的文章数量
BLUELOG_MANAGE_POST_PER_PAGE = 15
BLUELOG_COMMENT_PER_PAGE = 15