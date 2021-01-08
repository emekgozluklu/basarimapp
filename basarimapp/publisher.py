from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import get_user_by_email, get_exams
from basarimapp.auth import load_logged_in_user
import functools


bp = Blueprint('publisher', __name__, url_prefix='/publisher')


def publisher_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Login first.")
            return redirect(url_for('index'))
        elif "user_is_publisher" in session and not session["user_is_publisher"]:
            flash("You are not a publisher.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/dashboard')
@publisher_login_required
def dashboard():
    exams = get_exams(session["user_id"])
    load_logged_in_user()
    return render_template('publisher/dashboard.html', exams=exams)
