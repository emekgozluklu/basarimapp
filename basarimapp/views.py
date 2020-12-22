from flask import render_template, current_app, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import abort
from basarimapp.forms import *

# import forms
# import password handling tools
# import database handler class


def index():
        return render_template("index.html")


def login():
    form = LoginForm()  # request.form)
    if form.validate_on_submit():
        #user = User.query.filter_by(email=form.email.data).first()
        #if user is not None and user.verify_password(form.password.data):
        login_user(None)
        return redirect("index")

    return render_template('login.html', form=form)
