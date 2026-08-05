from flask import Blueprint
from flask import redirect, url_for

bp = Blueprint('main', __name__, url_prefix='/')

# 2026.08.04 by breeze start
@bp.route('/')
def index():
    return redirect(url_for('auth.login'))
# 2026.08.04 by breeze end