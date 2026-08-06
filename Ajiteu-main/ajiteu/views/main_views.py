from flask import Blueprint, g, redirect, render_template, url_for

from ajiteu.views.auth_views import login_required

bp = Blueprint('main', __name__, url_prefix='/')


@bp.route('/')
@login_required
def index():
    return render_template('main.html')


@bp.route('/my-posts')
@login_required
def my_posts():
    return render_template('main.html', page_mode='my_posts')