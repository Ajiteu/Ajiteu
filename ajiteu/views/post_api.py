from ajiteu import db
from ajiteu.models import Post, Comment, Reply, User, post_liker
from ajiteu.views.auth_views import login_required
from ajiteu.forms import PostForm, CommentForm # sinae : 808 CommentForm 추가
from flask import Blueprint, render_template, url_for, redirect, request, g, flash, current_app, jsonify
from datetime import datetime, timedelta
from sqlalchemy import func, distinct, or_
import os
import uuid
from werkzeug.utils import secure_filename


CATEGORY_KEYWORDS = {
    'travel': ['여행', 'trip', 'travel', '관광', '휴가', '해외', '국내여행'],
    'exercise': ['운동', 'exercise', '헬스', '러닝', '런닝', '요가', '필라테스', '근력'],
    'food': ['음식', 'food', '맛집', '요리', '먹방', '카페', '식당', '맛있'],
}


def build_category_filter(category: str):
    """본문 키워드로 카테고리 필터."""
    if not category or category == 'all':
        return None
    keywords = CATEGORY_KEYWORDS.get(category, [])
    if not keywords:
        return None
    return or_(*[Post.content.ilike(f'%{keyword}%') for keyword in keywords])


def get_weekly_trends(limit: int = 4):
    """최근 7일 게시글 중 좋아요 수 상위 글."""
    week_ago = datetime.now() - timedelta(days=7)
    posts = Post.query.filter(Post.create_date >= week_ago).all()
    posts.sort(key=lambda post: len(post.liker), reverse=True)
    return posts[:limit]
# from flask_login import current_user


bp = Blueprint('post', __name__, url_prefix='/post')
@bp.route('/list/<int:username_id>')
@login_required
def _list(username_id):
# @bp.route('/list/')
# def _list():
    user = User.query.get_or_404(username_id)
    print("__________________list user.username ==> ", user.username)

    page = request.args.get('page', type=int, default=1)
    #검색어
    kw = request.args.get('kw', type=str, default='')
    #정렬기준
    so = request.args.get('so', type=str, default='recent')
    category = request.args.get('category', type=str, default='all')

    post_list = Post.query

    category_filter = build_category_filter(category)
    if category_filter is not None:
        post_list = post_list.filter(category_filter)

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
                             Post.user.has(User.nickname.ilike(search)) |
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

    weekly_trends = get_weekly_trends(limit=4)

    return render_template(
        'main.html',
        post_list=post_list,
        page=page,
        kw=kw,
        so=so,
        user=user,
        current_category=category,
        weekly_trends=weekly_trends,
    )



@bp.route('/create/<int:username_id>', methods=('GET', 'POST'))
@login_required
def create(username_id):
    print("==============================create: ")
    user = User.query.get_or_404(username_id)
    form = PostForm()

    print(f"==============================create: {username_id}, {user.username}")
    print(f"Request method: {request.method}")
    print(f"Form errors: {form.errors}")


    # if request.method == 'POST':
    if request.method == 'POST' and form.validate_on_submit():
        #이미지파트
        image_files = form.image.data
        image_paths = []

        print("==============================POST if")

        #이미지 저장경로(오늘 날짜로 폴더 생성)
        today = datetime.now().strftime('%Y%m%d')
        upload_folder = os.path.join(current_app.root_path, 'static', 'photo', today)
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

        print("========================================post?")

        return redirect(url_for('post._list', username_id=user.id))
    return render_template('post_create.html', form=form, user=user)


@bp.route('/detail/<int:post_id>/')
@login_required
def detail(post_id):
    # sinae : 808 form 수정
    # form = PostForm()
    post_form = PostForm()
    comment_form = CommentForm()
    post = Post.query.get_or_404(post_id)
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()
    return render_template('post_detail.html', post=post, post_form=post_form, comment_form=comment_form)

@bp.route('modify/<int:post_id>/', methods=('GET', 'POST'))
@login_required
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
    return render_template('post_create.html', form=form, post=post, user=post.user)

@bp.route('/delete/<int:post_id>/')
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)
    if g.user != post.user:
        flash('삭제 권한이 없습니다')
        return redirect(url_for('post.detail', post_id=post_id))

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('post._list', username_id=g.user.id))       #sinae : 808 username_id=g.user.id 추가



# sinae 809 추천수정
@bp.route('/like/<int:post_id>/', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.get_or_404(post_id)

    if g.user == post.user:
        flash('본인이 작성한 글은 추천할 수 없습니다')
        return jsonify({'success': False, 'message': '본인이 작성한 글은 추천할 수 없습니다'})

    if g.user in post.liker:
        flash('이미 추천한 질문입니다')
        return jsonify({'success': False, 'message': '이미 추천한 질문입니다'})

    post.liker.append(g.user)
    db.session.commit()

    return jsonify({'success': True, 'message': '추천되었습니다', 'like_count': len(post.liker)})

# sinae 808 홈화면 모든글 보여주기

@bp.route('/', methods=['GET'])
def index():
    page = request.args.get('page', 1, type=int)
    post_list = Post.query.paginate(page=page, per_page=10)
    return render_template('main.html', post_list=post_list)

@bp.route('/user/<int:user_id>', methods=['GET'])
def user_posts(user_id):
    # sinae : 811 수정
    user = User.query.get_or_404(user_id)
    page = request.args.get('page', 1, type=int)
    post_list = Post.query.filter_by(user_id=user_id).order_by(Post.create_date.desc()).paginate(page=page, per_page=10)

    weekly_trends = get_weekly_trends(limit=4)

    return render_template('main.html', post_list=post_list, user=user, page=page, kw='', so='recent', current_category='all', weekly_trends=weekly_trends)