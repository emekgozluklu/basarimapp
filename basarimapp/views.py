from flask import render_template, current_app, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.exceptions import abort

# import forms
# import password handling tools
# import database handler class


def index():
        return render_template("index.html")
