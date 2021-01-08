import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import register_user, get_user_by_email, get_user_by_id
from basarimapp.forms import RegisterForm, LoginForm

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    error = None
    if g.user is None:
        return render_template('index.html', error="Login as admin.")
    return render_template('admin/dashboard.html', error=error)
