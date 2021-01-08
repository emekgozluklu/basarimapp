from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import register_user, get_user_by_email, get_user_by_id, get_publishers
from basarimapp.auth import load_logged_in_user
from basarimapp.forms import AddPublisherForm
from basarimapp import views
import functools


bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Login first.")
            return redirect(url_for('index'))
        elif "user_is_admin" in session and not session["user_is_admin"]:
            flash("You are not an admin.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/dashboard')
@admin_login_required
def dashboard():
    publishers = get_publishers()
    load_logged_in_user()
    return render_template('admin/dashboard.html', publishers=publishers)


@bp.route('/add/publisher', methods=('GET', 'POST'))
@admin_login_required
def add_publisher():
    pass
