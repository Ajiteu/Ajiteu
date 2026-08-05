from flask import Blueprint, render_template, request, url_for, redirect, g, flash
from datetime import datetime
from ajiteu import db
from ajiteu.forms import CommentForm, ReplyForm
from ajiteu.models import Post, Comment, Reply, User
# from team.views.auth_views import login_required

bp = Blueprint('reply', __name__, url_prefix='/reply')

#comment의 답변(reply) 등록
@bp.route('/create/comment/<int:comment_id>/', methods=('GET', 'POST'))
# @login_required
def create_reply(comment_id):
    form = ReplyForm()
    comment = Comment.query.get_or_404(comment_id)
    if request.method == 'POST' and form.validate_on_submit():
        reply = Reply(user=g.user, content=form.content.data, create_date=datetime.now(), comment=comment)
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('post.detail', post_id=comment.post.id))
    return render_template('reply.html', form=form)

#comment의 답변(reply) 수정
@bp.route('/modify/comment/<int:reply_id>/', methods=('GET', 'POST'))
# @login_required
def modify_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    if g.user != reply.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('post.detail', post_id=reply.comment.post.id))
    if request.method == 'POST':
        form = ReplyForm()
        if form.validate_on_submit():
            form.populate_obj(reply)
            reply.modify_date = datetime.now()
            db.session.commit()
            return redirect(url_for('post.detail', post_id=reply.comment.post.id))
    else:
        form = ReplyForm(obj=reply)
    return render_template('reply_form.html', form=form)

#comment의 답변(reply) 삭제
@bp.route('/delete/comment/<int:reply_id>/')
# @login_required
def delete_reply(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    post_id = reply.comment.post.id
    if g.user != reply.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(reply)
        db.session.commit()
    return redirect(url_for('post.detail', post_id=post_id))