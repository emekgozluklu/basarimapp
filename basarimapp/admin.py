from flask import Blueprint, flash, redirect, render_template, session, url_for
from basarimapp.dbmanager import (
    register_publisher, get_publishers, get_user_by_email, get_exams, delete_publisher, get_user_by_id
)
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


@bp.route('/')
@bp.route('/dashboard')
@admin_login_required
def dashboard():
    publishers = get_publishers()
    exam_count = dict()
    for pub in publishers:
        exam_count[pub[0]] = len(get_exams(pub[0]))  # get number of exams of the pub with id pub[0]
    load_logged_in_user()
    return render_template('admin/dashboard.html', publishers=publishers, exam_count=exam_count)


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


@bp.route('/delete_publisher/<publisher_id>')
@admin_login_required
def delete_publisher_view(publisher_id):
    pub = get_user_by_id(publisher_id)
    if pub is None:
        flash("Publisher not exists.!")
        return redirect(url_for("admin.dashboard"))
    else:
        delete_publisher(publisher_id)
        flash(f"Publisher with ID {publisher_id} is deleted!")
        return redirect(url_for("admin.dashboard"))
