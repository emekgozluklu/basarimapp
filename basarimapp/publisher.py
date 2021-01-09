from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.dbmanager import (
    get_user_by_email, get_exams, create_exam_template, create_examfield, activate_exam, get_publisher_of_exam,
    deactivate_exam
)
from basarimapp.auth import load_logged_in_user
from basarimapp.forms import AddExamForm, AddExamFieldForm
from basarimapp.exam import EXAM_TYPE_FIELDS, validate_exam_field_form
import functools


bp = Blueprint('publisher', __name__, url_prefix='/publisher')


def publisher_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash("Login first.")
            return redirect(url_for('index'))
        elif "user_is_publisher" in session and not session["user_is_publisher"]:
            flash("You are not a publisher.")
            return redirect(url_for('index'))
        return view(**kwargs)
    return wrapped_view


@bp.route('/dashboard')
@publisher_login_required
def dashboard():
    exams = get_exams(session["user_id"])
    load_logged_in_user()
    return render_template('publisher/dashboard.html', exams=exams)


@bp.route('/add_exam', methods=('GET', 'POST'))
@publisher_login_required
def add_exam():
    form = AddExamForm()
    error = None
    if form.validate_on_submit():
        title = form.title.data
        exam_type = form.exam_type.data

        if not title or exam_type is None:
            error = "Please fill all required fields."

        if error is None:
            exam_type = int(exam_type)
            fields = EXAM_TYPE_FIELDS[exam_type]

            session["fields"] = fields
            session["added_fields"] = 0

            exam_id = create_exam_template(session['user_id'], title, exam_type)
            session["exam_id"] = exam_id
            return redirect(url_for("publisher.add_examfield"))

    return render_template('publisher/add_exam.html', form=form, error=error)


@bp.route('/add_examfield', methods=('GET', 'POST'))
@publisher_login_required
def add_examfield():
    if "exam_id" not in session:
        flash("First fill the exam information...")
        return redirect(url_for("publisher.add_exam"))
    elif "added_fields" not in session or "fields" not in session:
        flash("Something went wrong...")
        return redirect(url_for("publisher.add_exam"))

    current_field_count = session["added_fields"]
    current_field_name = list(session["fields"].keys())[current_field_count]
    current_field_question_number = session["fields"][current_field_name]

    data = {
        "current_field_name": current_field_name,
        "current_field_question_number": current_field_question_number,
    }

    if request.method == "GET":
        return render_template('exam/answersheet.html', data=data)
    else:
        form_data = request.form
        if validate_exam_field_form(form_data, current_field_question_number):
            current_field_count += 1
            session["added_fields"] = current_field_count
            create_examfield(session["exam_id"], current_field_name, current_field_question_number, str(form_data.to_dict()))
            if current_field_count == len(session["fields"].keys()):
                activate_exam(session["exam_id"])
                session.pop("exam_id")
                session.pop("fields")
                session.pop("added_fields")
                return redirect(url_for("publisher.dashboard"))
            else:
                return redirect(url_for("publisher.add_examfield"))
        else:
            flash("Please fill all fields.")
            return render_template('exam/answersheet.html', data=data)


@bp.route('/deactivate/<exam_id>')
@publisher_login_required
def deactivate(exam_id):
    pub_id, is_active = get_publisher_of_exam(exam_id)
    if pub_id is None:
        flash("Not permitted!")
        return redirect(url_for("publisher.dashboard"))
    elif pub_id != session["user_id"]:
        return render_template('publisher/dashboard.html', error="Not permitted.")
    elif not is_active:
        return render_template('publisher/dashboard.html', error="Already inactive.")
    else:
        deactivate_exam(exam_id)
        return redirect(url_for("publisher.dashboard"))


@bp.route('/activate/<exam_id>')
@publisher_login_required
def activate(exam_id):
    pub_id, is_active = get_publisher_of_exam(exam_id)
    if pub_id is None:
        flash("Not permitted!")
        return redirect(url_for("publisher.dashboard"))
    elif pub_id != session["user_id"]:
        return render_template('publisher/dashboard.html', error="Not permitted.")
    elif is_active:
        return render_template('publisher/dashboard.html', error="Already active.")
    else:
        activate_exam(exam_id)
        return redirect(url_for("publisher.dashboard"))
