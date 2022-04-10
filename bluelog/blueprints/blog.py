from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, abort, make_response
from flask_login import current_user

from bluelog.emails import send_new_comment_mail, send_new_reply_email
from bluelog.extensions import db
from bluelog.forms import CommentForm, AdminCommentForm
from bluelog.models import Post, Category, Comment
from bluelog.utils import redirect_back

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items  # 获取查询到的分页文章列表
    return render_template('blog/index.html', pagination=pagination, posts=posts)


@blog_bp.route('/about')
def about():
    return render_template('blog/about.html')


# 某分类目录下的文章列表
@blog_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('blog/category.html', category=category, pagination=pagination, posts=posts)


# 查看文章详情
@blog_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    # 对文章评论进行分类, 可显示的评论必须是经过审核的
    pagintion = Comment.query.with_parent(post).filter_by(reviewed=True).order_by(Comment.timestamp.asc()) \
        .paginate(page, per_page)
    comments = pagintion.items

    if current_user.is_authenticated:
        # 当前用户是管理员
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.dat = current_app.config['BLUELOG_ADMIN_EMAIL']
        form.site.data = url_for('blog.index')
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author, email=email, site=site, body=body,
            from_admin=from_admin, reviewed=reviewed, post=post)
        replied_id = request.args.get('reply')
        # 如果该评论是一条回复，则从url的查询参数中获取被回复评论的id
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment  # 为关系属性赋值，建立关系
            send_new_reply_email(replied_comment)
        db.session.add(comment)
        db.session.commit()

        if current_user.is_authenticated:  # 对于管理员做出的评论不发送邮件
            flash('Comment publised', 'success')
        else:
            # 匿名用户的评论给管理发邮件
            flash('Thanks, your comment will be published after reviewed.', 'info')
            send_new_comment_mail(post)
        return redirect(url_for('.show_post', post_id=post_id))

    return render_template('blog/post.html', post=post, pagination=pagintion, comments=comments, form=form)


# @blog_bp.route('/post/<slug>')
# def show_slug_post(slug):
#     """通过slug来查询文章"""
#     post = Post.query.filter_by(slug=slug).first_or_404()
#     return redirect(url_for('.show_post', post_id=post.id))


@blog_bp.route('/reply/comment/<int:comment_id>')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post_id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')


@blog_bp.route('/change-theme/<theme_name>')
def change_theme(theme_name):
    if theme_name not in current_app.config['BLUELOG_THEMES'].keys():
        abort(404)

    # 将设置的主题名称添加到cookies中
    response = make_response(redirect_back())
    response.set_cookie('theme', theme_name, max_age=30 * 24 * 60 * 60)  # 有效期30天
    return response
