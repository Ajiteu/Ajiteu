from ajiteu import db
from ajiteu.models import Post, Comment, Reply, User
from ajiteu.forms import CommentForm
from datetime import datetime
from flask import Blueprint, url_for, request, redirect, render_template, g, flash

bp = Blueprint('comment', __name__, url_prefix='/comment')

@bp.route('/create/<int:post_id>/', methods=('POST',))
# @login_required
def create(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        content = request.form['content']
        comment = Comment(content=content, create_date=datetime.now(), user=g.user)
        post.comment_set.append(comment)
        db.session.commit()

        #앵커 없는버전
        return redirect(url_for('post.detail', post_id=post_id))
        #앵커 있는버전
        #return redirect('{}#comment_{}'.format(url_for('detail', post_id=post_id), comment.id))
    return render_template('detail.html', post=post, form=form)

@bp.route('/modify/<int:comment_id>/', methods=('GET', 'POST'))
# @login_required
def modify(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if g.user != comment.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('post.detail', post_id=comment.post.id))

    if request.method == 'POST':
        form = CommentForm()
        if form.validate_on_submit():
            form.populate_obj(comment)
            db.session.commit()

            #앵커 없는버전
            return redirect(url_for('post.detail', post_id=comment.post.id))
            #앵커 있는 버전
            #return redirect('{}#comment_{}'.format(url_for('detail', post_id=comment.post.id), comment.id))
    else:
        form = CommentForm(obj=comment)
    #comment.edit
    return render_template('', comment=comment, form=form)

@bp.route('/delete/<int:comment_id>/')
# @login_required
def delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id
    if g.user != comment.user:
        flash('삭제권한이 없습니다')
    else:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('post.detail', post_id=post_id))

@bp.route('/liker/<int:comment_id>/')
# @login_required
def liker(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post.id

    #본인 댓글 추천 방지
    if g.user == comment.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
        return redirect(url_for('post.detail', post_id=post_id))

    #중복 추천 방지
    if g.user in comment.liker:
        flash('이미 추천한 질문입니다')
        return redirect(url_for('post.detail', post_id=post_id))

    #추천
    comment.liker.append(g.user)
    db.session.commit()

    return redirect(url_for('post.detail', post_id=post_id))    