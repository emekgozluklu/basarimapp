import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import register_user, get_user_by_email, get_user_by_id
from basarimapp.forms import RegisterForm, LoginForm
from basarimapp import views

bp = Blueprint('admin', __name__, url_prefix='/admin')

"""@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
        g.admin_user = False
    else:
        g.user = get_user_by_id(user_id)
        g.admin_user = g.user[5]
        print(g.user)
"""


@bp.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    if 'user_id' not in session:
        flash("Login first.")
        return redirect(url_for('index'))
    elif "user_is_admin" in session and not session["user_is_admin"]:
        flash("You are not an admin.")
        return redirect(url_for('index'))

    return render_template('admin/dashboard.html')
