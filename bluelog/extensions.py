from flask_bootstrap import Bootstrap4
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

bootstrap = Bootstrap4()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()


@login_manager.user_loader
def load_user(user_id):
    """根据session中的user_id返回用户对象 == current_user"""
    from bluelog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'  # 登录操作视图函数端点，未登录的用户访问@login_required的视图，跳转到该端点
login_manager.login_message = '请先登录再进行操作!'  # 未登录的用户访问@login_required的视图，返回该消息
login_manager.login_message_category = 'warning'  # 消息类别
