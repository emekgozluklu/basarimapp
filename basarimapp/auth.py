import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from basarimapp.dbmanager import register_user, get_user_by_email, get_user_by_id
from basarimapp.forms import RegisterForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_user_by_id(user_id)


@bp.route('/register', methods=('GET', 'POST'))
def register():

    if 'user_id' in session:
        return redirect(url_for("index"))

    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data

        u = get_user_by_email(email)

        if not first_name or not last_name or not email or not password or not confirm:
            error = "Please fill all required fields."
        elif password != confirm:
            error = "Passwords do not match."
        elif u is not None:
            error = "Account with given email already exists."
        if error is None:
            password_hash = generate_password_hash(password)
            register_user(first_name, last_name, email, password_hash)
            session.clear()
            session["user_id"] = u[0]
            session["user_is_admin"] = False
            session["user_is_publisher"] = False
            return redirect(url_for("index"))

    return render_template('auth/register.html', form=form, error=error)


@bp.route('/login', methods=('GET', 'POST'))
def login():

    if 'user_id' in session:
        return redirect(url_for("index"))

    form = LoginForm()
    error = None
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = get_user_by_email(email)
        if user is None:
            error = "User does not exist! Maybe you should register first?"
        elif not check_password_hash(user[4], password):
            error = "Incorrect password!"
        if error is None:
            session.clear()
            session["user_id"] = user[0]
            session["user_is_admin"] = user[5]
            session["user_is_publisher"] = user[6]
            return redirect(url_for("index"))
    return render_template("auth/login.html", form=form, error=error)


@bp.route('/logout')
def logout():
    if 'user_id' in session:
        session.clear()
        flash("Logged out.")
        return redirect(url_for("index"))

    return redirect(url_for('index'))


"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return render_template("auth/not_permitted.html")
        return view(**kwargs)
    return wrapped_view
"""
