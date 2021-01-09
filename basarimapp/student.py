from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.auth import load_logged_in_user, login_required
from basarimapp.forms import EnterExamCodeForm
from basarimapp.exam import EXAM_TYPE_FIELDS, EXAM_TYPES
import functools


bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    load_logged_in_user()
    # exam_data = get_exam_data_of_student(session["user_id"])
    return render_template('student/dashboard.html')


@bp.route("/code", methods=('GET', 'POST'))
@login_required
def enter_code():
    form = EnterExamCodeForm()
    if form.validate_on_submit():

        code = form.code.data

        exam = None
        # exam = get_exam_by_code(code)
        if code is None:
            error = "Something is wrong. Log in again or contact us."
            flash(error)
            session.clear()
            return redirect(url_for('auth.logout'))
        elif exam is None:
            error = "Looks like this code is wrong. Please check it and enter again."
            return render_template("student/enter_code.html", form=form, error=error)
        elif not exam[5]:
            error = "Looks like this exam is inactive. Please check it and enter again."
            return render_template("student/enter_code.html", form=form, error=error)
        else:
            session["exam_id"] = exam[0]
            session["added_fields"] = 0

            exam_type = int(int(exam[4]))
            session["fields"] = EXAM_TYPE_FIELDS[exam_type]

            # START TO FILL THE ANSWER SHEET
            flash("Exam exist. you can start to fill.")
            return redirect(url_for("student.dashboard"))
    return render_template("student/enter_code.html", form=form)
