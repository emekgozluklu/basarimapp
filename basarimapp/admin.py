from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import register_publisher, get_publishers, get_user_by_email
from basarimapp.auth import load_logged_in_user
from basarimapp.forms import AddPublisherForm
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


@bp.route('/add_publisher', methods=('GET', 'POST'))
@admin_login_required
def add_publisher():
    form = AddPublisherForm()
    error = None
    if form.validate_on_submit():
        pub_name = form.pub_name.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data

        u = get_user_by_email(email)

        if not pub_name or not email or not password or not confirm:
            error = "Please fill all required fields."
        elif password != confirm:
            error = "Passwords do not match."
        elif u is not None:
            error = "Account with given email already exists."
        if error is None:
            register_publisher(pub_name, email, password)
            return redirect(url_for("admin.dashboard"))

    return render_template('admin/add_publisher.html', form=form, error=error)
