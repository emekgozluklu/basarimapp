from flask import render_template, redirect, url_for
from basarimapp.forms import LoginForm, RegisterForm
from basarimapp.dbmanager import DBManager
from werkzeug.security import generate_password_hash

# from flask_login import login_user, logout_user, current_user, login_required
# import password handling tools
# import database handler class
# import forms


def index():
    return render_template("index.html")


def login():
    form = LoginForm()  # request.form)
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        # if user is not None and user.verify_password(form.password.data):
        # login_user(None)
        return redirect("index")

    return render_template('login.html', form=form)


def register():
    form = RegisterForm()
    if form.validate_on_submit():
        """
        db = DBManager()
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        confirm = form.confirm.data
        print(first_name, last_name, email, password, confirm)
        if password != confirm:
            return render_template('register.html', form=form, errors="Passwords not matching.")
        # password = generate_password_hash(password)
        db.insert("userrole", f"(DEFAULT, '{first_name}', '{last_name}', '{email}', '00000000', '{password[:15]}', DEFAULT, DEFAULT, DEFAULT, DEFAULT, DEFAULT)")
        """
        return redirect(url_for('index'))
    return render_template('register.html', form=form)
