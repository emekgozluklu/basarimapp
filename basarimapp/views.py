from flask import render_template, redirect, url_for
from basarimapp.forms import LoginForm, RegisterForm

# from flask_login import login_user, logout_user, current_user, login_required
# from werkzeug.exceptions import abort
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
        new_user = User(email=form.email.data,
                username=form.username.data,
                password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        """
        return redirect(url_for('index'))
    return render_template('register.html', form=form)
