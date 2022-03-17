from threading import Thread

from flask import url_for, current_app
from flask_mail import Message

from bluelog.extensions import mail


def _send_async_mail(app, message):
    # 使用app程序上下文
    with app.app_context():
        mail.send(message)


def send_mail(subject, to, html):
    # 通过代理对象获取真正的app程序实例
    app = current_app._get_current_object()
    message = Message(subject, recipients=[to], html=html)
    thr = Thread(target=_send_async_mail, args=(app, message))
    thr.start()
    return thr


def send_new_comment_mail(post):
    """当有新评论时，给管理员发送邮件提醒"""
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'  # 使用片段标识符定位到页面中元素id=comments的部分
    send_mail(subject='New comment',
              to=current_app.config['BLUELOG_ADMIN_EMAIL'],
              html="""
              <p>New comment in post <i>%s</i>, click the link below to ckeck:</p>
              <p><a href="%s">%s</a></p>
              <p><small style="color: #868e96">Do not reply this email.</small></p>
              """ % (post.title, post_url, post_url))


def send_new_reply_email(comment):
    """当用户的评论被回复时，发邮件提醒用户"""
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True)
    send_mail(subject='New reply',
              to=comment.email,  # 发表评论的用户的邮箱
              html="""
              <p>New reply for the comment you left in post <i>%s</i>, click the link below to ckeck:</p>
              <p><a href="%s">%s</p>
              <p><small style="color: #868e96">Do not reply this email.</small></p> 
              """ % (comment.post.title, post_url, post_url))
