import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from basarimapp.dbmanager import register_user, get_user
from basarimapp.forms import RegisterForm, LoginForm

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data

        if not first_name or not last_name or not email or not password or not confirm:
            error = "Please fill all required fields."
        elif password != confirm:
            error = "Passwords not matching."
        elif get_user(email) is None:
            error = "Account with given email already exists."
        if error is None:
            password = generate_password_hash(password)
            register_user(first_name, last_name, email, password)
            return redirect(url_for('index'))

    return render_template('auth/register.html', form=form, error=error)


@bp.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = get_user(email)
        if user is None:
            error = "User does not exist! Maybe you should register first?"

        elif not check_password_hash(user[4], password):
            error = "Incorrect password!"
        if error is None:
            session.clear()
            session["user_id"] = user[0]
            return redirect(url_for("index"))
    return render_template("auth/login.html", form=form, error=error)
