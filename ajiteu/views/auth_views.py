from flask import Blueprint, render_template, request, url_for, redirect, flash, session, g #session, g 추가
from werkzeug.security import generate_password_hash, check_password_hash
from ajiteu import db
from ajiteu.forms import UserCreateForm, UserLoginForm
from ajiteu.models import User
import functools    # 함수 도구 모률 임포트



bp = Blueprint('auth', __name__, url_prefix='/auth')

# 회원등록
@bp.route('/signup/', methods=('GET', 'POST'))
def signup():
    form = UserCreateForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            # 2026.08.04 by breeze start
            image_path = 'images/default.png'       # by breeze - 2026.08.07
            user = User(username=form.username.data,
                        password=generate_password_hash(form.password1.data),
                        email=form.email.data,
                        nickname=form.username.data,
                        image_path=image_path)      # by breeze - 2026.08.07
            # 2026.08.04 by breeze end
            db.session.add(user)
            db.session.commit()

            #회원가입 성공 후 자동 로그인
            session.clear()
            session['user_id'] = user.id

            return redirect(url_for('main.index'))
        else:
            print('이미 존재하는 사용자입니다.')
            flash('이미 존재하는 사용자입니다.')
    return render_template('auth/signup.html', form=form)

# 로그인
@bp.route('/login/', methods=('GET', 'POST'))
def login():
    print("*" * 50)
    print("auth_view.py==>login")
    print("*" * 50)

    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        error = None
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            error = "존재하지 않는 사용자입니다."
            print(error)
        elif not check_password_hash(user.password, form.password.data):
            error = "비밀번호가 올바르지 않습니다"
            print(error)
        if error is None:
            session.clear()
            session['user_id'] = user.id
            print("goto====> post._list")
            # by breeze - 2026.08.06
            return redirect(url_for('post._list', username_id=user.id))
        flash(error)
    print("login =====> none")
    return render_template('auth/login.html', form=form)
    # return render_template('main.html', form=form)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))


# 사용자 로그인 정보를 g.user 변수에 저장
# @bp.before_app_request: 어떤 라우트 함수가 실행되더라도 그 전에 세션을 검사함
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


# 비인증 회원일 경우 로그인 주소(/auth/login/)로 보내는 데코레이션 로직
def login_required(view):
    # Flask의 라우팅,  디버깅, 문서화 등에 필요한 원래 함수의 메타데이터(이름, 설명, 모듈 정보 등)를 보존
    @functools.wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(*args, **kwargs)
    return wrapped_view



