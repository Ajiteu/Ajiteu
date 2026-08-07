from ajiteu import db
from ajiteu.models import Post, Comment,Reply, User, post_liker
from ajiteu.forms import ProfileForm
from flask import Blueprint, render_template, url_for, redirect, request, g, flash, current_app, session
from datetime import datetime
from sqlalchemy import func, distinct
import os
import uuid
from werkzeug.utils import secure_filename
from ajiteu.views.auth_views import login_required    # 데코레이터 임포트


bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)

@bp.route('/detail/<int:username_id>/', methods=('GET', 'POST'))
@login_required
def detail(username_id):
    user = User.query.get_or_404(username_id)
    form = ProfileForm(obj=user)

    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.user_intro = form.user_intro.data

        image_file = form.image.data
        if image_file:
            today = datetime.now().strftime('%Y%m%d')
            upload_folder = os.path.join(current_app.root_path, 'static/images', today)
            os.makedirs(upload_folder, exist_ok=True)

            ext = os.path.splitext(image_file.filename)[1]
            filename = f"{uuid.uuid4()}{ext}"

            file_path = os.path.join(upload_folder, filename)
            image_file.save(file_path)

            user.image_path = f'images/{today}/{filename}'

        db.session.commit()
        # flash('프로필이 저장되었습니다.')
        return redirect(url_for('post._list', username_id=user.id))

    return render_template('profile.html', user=user, form=form)