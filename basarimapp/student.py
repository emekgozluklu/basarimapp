from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from basarimapp.auth import load_logged_in_user, login_required
from basarimapp.forms import EnterExamCodeForm
from basarimapp.exam import EXAM_TYPE_FIELDS, EXAM_TYPES, validate_answersheet_form
from basarimapp.dbmanager import (
    add_choices_to_answersheet, get_exam_by_code, create_answersheet_template, calculate_result,
    get_joined_result_data, get_field_results_of_student
)
import functools


bp = Blueprint('student', __name__, url_prefix='/student')


@bp.route('/exams')
@login_required
def exams():
    load_logged_in_user()
    results = get_joined_result_data(session["user_id"])
    return render_template('student/exams.html', results=results, exam_types=EXAM_TYPES)


@bp.route("/code", methods=('GET', 'POST'))
@login_required
def enter_code():
    form = EnterExamCodeForm()
    if form.validate_on_submit():
        code = form.code.data
        exam = get_exam_by_code(code)  # fetch the exam or None if code is invalid
        if code is None:
            error = "Something is wrong. Log in again or contact us."
            flash(error)
            session.clear()
            return redirect(url_for('auth.logout'))
        elif exam is None:
            error = "Looks like this code is wrong. Please check it and enter again."
            return render_template("student/enter_code.html", form=form, error=error)
        elif not exam[5]:  # check whether exam is active or not
            error = "Looks like this exam is inactive. Please check it and enter again."
            return render_template("student/enter_code.html", form=form, error=error)
        else:
            session["exam_id"] = exam[0]
            session["added_fields"] = 0

            exam_type = int(int(exam[4]))
            session["fields"] = EXAM_TYPE_FIELDS[exam_type]

            sheet_id = create_answersheet_template(session["user_id"], session["exam_id"])
            session["sheet_id"] = sheet_id

            return redirect(url_for("student.fill_sheet"))
    return render_template("student/enter_code.html", form=form)


@bp.route("/fill", methods=('GET', 'POST'))
@login_required
def fill_sheet():
    if "sheet_id" not in session:
        flash("First enter the exam code.")
        return redirect(url_for("student.enter_code"))
    elif "added_fields" not in session or "fields" not in session:
        flash("Something went wrong")
        return redirect(url_for("student.dashboard"))

    index_of_field = session["added_fields"]
    name_of_field = list(session["fields"].keys())[index_of_field]
    num_of_questions = session["fields"][name_of_field]

    template_data = {
        "field_name": name_of_field,
        "num_of_questions": num_of_questions,
    }

    if request.method == "GET":
        return render_template("student/answersheet.html", data=template_data)
    else:
        form_data = request.form.to_dict()
        if validate_answersheet_form(form_data, num_of_questions):
            index_of_field += 1
            session["added_fields"] = index_of_field
            add_choices_to_answersheet(session["sheet_id"], form_data, name_of_field)
            if index_of_field == len(session["fields"]):
                calculate_result(session["user_id"], session["sheet_id"], session["exam_id"])
                session.pop("exam_id")
                session.pop("sheet_id")
                session.pop("fields")
                session.pop("added_fields")
                return redirect(url_for("student.dashboard"))
            else:
                return redirect(url_for("student.fill_sheet"))
        else:
            flash("Form is corrupted. Fill again.")
            return render_template("student/answersheet.html", data=template_data)


@bp.route('/')
@bp.route('/dashboard')
@login_required
def dashboard():
    error = None
    load_logged_in_user()

    last_week, last_month, general = get_field_results_of_student(session["user_id"])

    if general[1] is None or not last_week or not last_month:
        error = "You do not have any exams for now. Start uploading..."
        last_week = last_month = [("", 0, 0, 0, 0, 1)]
        general = [0, 0]

    lecture_names_month = [i[0] for i in last_month]
    lecture_names_week = [i[0] for i in last_week]

    query_size = len(last_month[0])

    # fill empty lectures
    for lec in lecture_names_month:
        if lec not in lecture_names_week:
            last_week.append(tuple([lec] + [0 for _ in range(query_size - 1)]))

    num_of_lectures = len(last_month)

    data = {
        "last_week": sorted(last_week, key=lambda x: x[0]),
        "last_month": sorted(last_month, key=lambda x: x[0]),
        "num_of_lectures": num_of_lectures,
        "general": general
    }
    print(sorted(last_week, key=lambda x: x[0]), sorted(last_month, key=lambda x: x[0]))
    for i in range(num_of_lectures):
        if data["last_month"][i][0] != data["last_week"][i][0]:
            raise Exception("There is something wrong with orders. ")

    return render_template('student/dashboard.html', data=data, error=error)
