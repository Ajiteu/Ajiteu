from ajiteu import db
from ajiteu.models import Post, Comment,Reply, User, post_liker
#from team import login_required
from ajiteu.forms import PostForm
from flask import Blueprint, render_template, url_for, redirect, request, g, flash, current_app
from datetime import datetime
from sqlalchemy import func, distinct
import os
import uuid
from werkzeug.utils import secure_filename


bp = Blueprint('post', __name__, url_prefix='/post')

@bp.route('/list')
def _list():
    page = request.args.get('page', type=int, default=1)
    #검색어
    kw = request.args.get('kw', type=str, default='')
    #정렬기준
    so = request.args.get('so', type=str, default='recent')

    post_list = Post.query

    #검색조건 1. (kw)
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = (db.session.query(Comment.post_id, Comment.content, User.username)
                     .join(User, Comment.user_id == User.id).subquery())

        post_list = (post_list
                     .outerjoin(sub_query, sub_query.c.post_id == Post.id)
                     .filter(Post.content.ilike(search) |
                             sub_query.c.content.ilike(search) |
                             Post.user.has(User.username.ilike(search)) |
                             sub_query.c.username.ilike(search)))
    #검색조건 2. (so) - 임시
    if so == 'recommend':
        post_list = (post_list
                     .outerjoin(post_liker, Post.id == post_liker.c.post_id)
                     .groupby(Post.id)
                     .order_by(func.count(distinct(Comment.id)).desc(), Post.create_date.desc()))

    elif so == 'popular':
        #Comment순
        post_list = (post_list
                     .outerjoin(Comment, Comment.post_id == Post.id)
                     .group_by(Post.id)
                     .order_by(func.count(distinct(Comment.id)).desc(), Post.create_date.desc()))

    else:
        #최신순
        post_list = (post_list
                     .group_by(Post.id)
                     .order_by(Post.create_date.desc()))

    post_list = post_list.paginate(page=page, per_page=10)

    return render_template('main.html', post_list=post_list, page=page, kw=kw, so=so)



@bp.route('/create/', methods=('GET', 'POST'))
def create():
    form = PostForm()
    if request.method == 'POST' and form.validate_on_submit():
        #이미지파트
        image_files = form.image.data
        image_paths = []

        #이미지 저장경로(오늘 날짜로 폴더 생성)
        today = datetime.now().strftime('%Y%m%d')
        upload_folder = os.path.join(current_app.root_path, '', today)
        os.makedirs(upload_folder, exist_ok=True)

        #이미지 파일 존재시
        if image_files:
            for image_file in image_files:
                if image_file and image_file.filename != '':
                    ext = os.path.splitext(image_file.filename)[1]
                    filename = f'{uuid.uuid4()}{ext}'
                    file_path = os.path.join(upload_folder, filename)
                    image_file.save(file_path)

                    #DB용 상대경로 리스트에 추가
                    image_paths.append(f'photo/{today}/{filename}')

        joined_image_paths = ",".join(image_paths) if image_paths else None

        
        post = Post(content=form.content.data,
                        create_date=datetime.now(),
                        user=g.user, 
                        image_path=joined_image_paths)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('post._list'))
    return render_template('post_create.html', form=form)


@bp.route('/detail/<int:post_id>/')
def detail(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post, form=form)

@bp.route('modify/<int:post_id>/', methods=('GET', 'POST'))
# @login_required
def modify(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('post.detail', post_id=post_id))

    if request.method == 'POST':
        form = PostForm()
        if form.validate_on_submit():
            form.populate_obj(post)
            db.session.commit()
            return redirect(url_for('post.detail', post_id=post_id))
    else:
        form = PostForm(obj=post)
    return render_template('edit.html', form=form)

@bp.route('/delete/<int:post_id>/')
# @login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.user:
        flash('삭제 권한이 없습니다')
        return redirect(url_for('post.detail', post_id=post_id))
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('post._list'))


#추후 수정-------------------------------

@bp.route('/like/<int:post_id>/')
# @login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user == post.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
        return redirect(url_for('post.detail', post_id=post_id))

    if g.user in post.liker:
        flash('이미 추천한 질문입니다')
        return redirect(url_for('post.detail', post_id=post_id))

    post.liker.append(g.user)
    db.session.commit()

    return redirect(url_for('post.detail', post_id=post_id))

