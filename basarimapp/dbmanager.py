from flask import current_app
from werkzeug.security import generate_password_hash
from decouple import config
import psycopg2
import os
import string
import random
from basarimapp.exam import check_answers

curdir = os.getcwd()
fn = os.path.join(curdir, "db_structure.sql")
DB_INITIAL_QUERY = open(fn, "r").read()
TABLE_NAMES = ["USERROLE", "EXAM", "EXAMFIELD", "RESULT", "FIELDRESULT", "ANSWERSHEET"]

REGISTER_USER_STATEMENT = """
INSERT INTO userrole (first_name, last_name, email, password_hash, is_admin, is_publisher)
VALUES (%s, %s, %s, %s, %s, %s);
"""

CREATE_EXAM_TEMPLATE_STATEMENT = """
INSERT INTO exam (publisher_id, title, code, type, is_active)
VALUES (%s, %s, %s, %s, %s);
"""

CREATE_EXAMFIELD_TEMPLATE_STATEMENT = """
INSERT INTO examfield (exam_id, field_name, num_of_question, answer_list)
VALUES (%s, %s, %s, %s);
"""

CREATE_RESULT_STATEMENT = """
INSERT INTO result (userrole_id, exam_id, sheet_id)
VALUES (%s, %s, %s);
"""

UPDATE_RESULT_STATEMENT = """
UPDATE result
SET corrects = %s,
wrongs = %s,
unaswereds = %s,
net = %s
WHERE sheet_id = %s;
"""

ACTIVATE_EXAM_STATEMENT = """
UPDATE exam
SET is_active = true
WHERE id = %s ;
"""

DEACTIVATE_EXAM_STATEMENT = """
UPDATE exam
SET is_active = false
WHERE id = %s ;
"""

DELETE_USER_BY_ID_STATEMENT = """
DELETE FROM userrole
WHERE id = %s ;
"""

CREATE_SHEET_TEMPLATE_STATEMENT = """
INSERT INTO answersheet (userrole_id, exam_id, answers)
VALUES (%s, %s, %s);
"""


def del_db(app):
    with app.app_context():
        url = current_app.config['DATABASE']
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                for table in TABLE_NAMES:
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")


def init_db(app, override=False):
    if override:
        del_db(app)
    with app.app_context():
        url = current_app.config['DATABASE']
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(DB_INITIAL_QUERY)


def register_user(first_name, last_name, email, password, is_admin=False, is_publisher=False):
    p_hash = generate_password_hash(password)
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(REGISTER_USER_STATEMENT, (
                first_name, last_name, email, p_hash, is_admin, is_publisher
            ))


def get_user_by_email(email):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE email = %s", (email,))
            res = cur.fetchone()
    return res


def get_user_by_id(uid):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE id = %s", (uid,))
            res = cur.fetchone()
    return res


def create_super_user(app):
    print("Creating superuser...")
    first_name = "admin"
    last_name = "admin"
    is_admin = True
    is_publisher = False
    with app.app_context():
        email = config("ADMIN_EMAIL")
        p_hash = generate_password_hash(config("ADMIN_PASSWORD"))
        url = app.config['DATABASE']
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute(REGISTER_USER_STATEMENT, (
                        first_name, last_name, email, p_hash, is_admin, is_publisher
                    ))
                    print(f"Superuser created. Email= {email}")
                except psycopg2.errors.UniqueViolation:
                    print(f"Already exists! Email= {email}")


def register_publisher(pub_name, email, password, is_admin=False, is_publisher=True):
    p_hash = generate_password_hash(password)
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(REGISTER_USER_STATEMENT, (
                pub_name, "", email, p_hash, is_admin, is_publisher
            ))


def get_publishers():
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE is_publisher = %s", ('true',))
            res = cur.fetchall()
    return res


def get_exams(pub_id):
    # connection sessionda tutulabilir hızlandırmak için
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM exam WHERE publisher_id = %s;", (pub_id,))
            res = cur.fetchall()
    return res


def create_exam_template(pub_id, title, exam_type):
    url = current_app.config['DATABASE']
    code = ''.join(random.choices(string.ascii_uppercase, k=10))  # 10 chars random key
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(CREATE_EXAM_TEMPLATE_STATEMENT, (
                    pub_id, title, code, exam_type, False
                ))
            except psycopg2.errors.UniqueViolation:
                code = ''.join(random.choices(string.ascii_uppercase, k=10))  # 10 chars random key
                cur.execute(CREATE_EXAM_TEMPLATE_STATEMENT, (
                    pub_id, title, code, exam_type, False
                ))
            cur.execute("SELECT * FROM exam WHERE code = %s;", (code,))  # select created exam
            res = cur.fetchone()  # fetch it
    return res[0]  # return exam id


def create_examfield(exam_id, field_name, num_of_q, answer_list):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_EXAMFIELD_TEMPLATE_STATEMENT, (
                exam_id, field_name, num_of_q, answer_list
            ))


def activate_exam(exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(ACTIVATE_EXAM_STATEMENT, (exam_id,))


def deactivate_exam(exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(DEACTIVATE_EXAM_STATEMENT, (exam_id,))


def get_publisher_of_exam(exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT (publisher_id, is_active) FROM exam WHERE id = %s;", (exam_id,))
            res = cur.fetchone()

    if res is not None:
        res = res[0].strip("()").split(",")
        pub_id = int(res[0])
        is_active = res[1] == "t"
    else:
        pub_id = None
        is_active = None
    return pub_id, is_active


def delete_publisher(pub_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_USER_BY_ID_STATEMENT, (pub_id, ))


def get_results_of_student(student_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM result WHERE userrole_id = %s;", (student_id, ))
            res = cur.fetchall()
    return res


def create_answersheet_template(user_id, exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_SHEET_TEMPLATE_STATEMENT, (
                user_id, exam_id, ""
            ))

            cur.execute("SELECT * FROM answersheet WHERE (userrole_id = %s AND exam_id = %s);", (user_id, exam_id))
            res = cur.fetchone()  # fetch it
    return res[0]


def get_exam_by_code(exam_code):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM exam WHERE code = %s;", (exam_code,))
            res = cur.fetchone()
    return res


def add_choices_to_answersheet(sheet_id, form_data, field_name):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            # get the sheet from db first
            cur.execute("SELECT * FROM answersheet WHERE id = %s;", (sheet_id,))
            res = cur.fetchone()

            # this should not occur.
            if res is None:
                raise Exception("Add choices crashed hard.")

            # read already submitted answers and add new form data to them
            previous_answers = res[3]  # already submitted answers
            if previous_answers:
                answers_dict = eval(previous_answers)  # convert to dictionary
                answers_dict[field_name] = form_data  # add new form with field name
            else:
                answers_dict = dict()  # create dict
                answers_dict[field_name] = form_data  # insert the form data

            # write changes to database, update with new answers
            cur.execute("UPDATE answersheet SET answers = %s WHERE id = %s;", (str(answers_dict), sheet_id))


def calculate_result(user_id, sheet_id, exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            # create result in database
            cur.execute(CREATE_RESULT_STATEMENT, (user_id, exam_id, sheet_id))

            cur.execute("SELECT * FROM result WHERE sheet_id = %s;", (sheet_id,))
            result = cur.fetchone()

            # this should not occur.
            if result is None:
                raise Exception("Calculate result crashed hard.")

            total_corrects = 0
            total_wrongs = 0
            total_unanswereds = 0

            # get the sheet from db
            cur.execute("SELECT * FROM answersheet WHERE id = %s;", (sheet_id,))
            sheet = cur.fetchone()

            # this should not occur.
            if sheet is None:
                raise Exception("Calculate result crashed hard.")

            # read already submitted answers and add new form data to them
            answers = sheet[3]  # already submitted answers
            if not answers:
                raise Exception("Error while calculating result. No answer.")
            answers = eval(answers)
            fields = answers.keys()

            for field in fields:
                cur.execute("SELECT * FROM examfield WHERE exam_id = %s AND field_name = %s;", (exam_id, field))
                exam_field = cur.fetchone()

                if exam_field is None:
                    raise Exception("examfield can not be found in the database.")

                correct_answers = eval(exam_field[4])
                field_corrects, field_wrongs, field_unanswereds = check_answers(correct_answers, answers[field])

                total_corrects += field_corrects
                total_wrongs += field_wrongs
                total_unanswereds += field_unanswereds

            net = total_corrects - 0.25*total_wrongs
            cur.execute(UPDATE_RESULT_STATEMENT, (total_corrects, total_wrongs, total_unanswereds, net, sheet_id))


if __name__ == "__main__":
    print("Reinitializing database.")
    from basarimapp import create_app
    a = create_app()
    init_db(a, override=True)
    print("Done!")
