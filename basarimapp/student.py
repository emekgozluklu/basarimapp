from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.auth import load_logged_in_user, login_required
import functools


bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    load_logged_in_user()
    return render_template('student/dashboard.html')
