from flask import current_app
from werkzeug.security import generate_password_hash
from decouple import config
import psycopg2
import os
import string
import random
from basarimapp.exam import check_answers

fn = os.path.join(".", "db_structure.sql")
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
unanswereds = %s,
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

JOIN_USER_RESULT_EXAM = """
SELECT
    exam.title,
    exam.type,
    pub.first_name,
    result.corrects,
    result.wrongs,
    result.unanswereds,
    result.net,
    result.score,
    result.upload_time,
    result.is_active,
    result.id
FROM
     userrole AS stu
INNER JOIN result
    ON stu.id = result.userrole_id
INNER JOIN exam
    ON result.exam_id = exam.id
INNER JOIN userrole AS pub
    ON exam.publisher_id = pub.id
WHERE
      stu.id = %s
ORDER BY
    result.upload_time DESC;
"""

NUM_OF_UPLOADED_EXAMS_TODAY = """
SELECT count(*)
FROM result
WHERE upload_time > now() - interval '1 day' AND userrole_id = %s;
"""

NUM_OF_UPLOADED_EXAMS_THIS_WEEK = """
SELECT count(*)
FROM result
WHERE upload_time > now() - interval '1 week' AND userrole_id = %s;
"""

NUM_OF_UPLOADED_EXAMS_THIS_MONTH = """
SELECT count(*)
FROM result
WHERE upload_time > now() - interval '1 month' AND userrole_id = %s;
"""

GET_FIELD_RESULTS_STATEMENT = """
SELECT
    count(r.id),
    sum(r.corrects)+sum(r.wrongs)+sum(r.unanswereds) AS ques
FROM
     result AS r
WHERE userrole_id = %s AND is_active = true AND exam_id is not null;
"""

GET_FIELD_RESULTS_LAST_WEEK = """
SELECT
    e.field_name,
    count(e.field_name),
    sum(f.corrects::INTEGER),
    sum(f.wrongs::INTEGER),
    sum(f.unanswereds::INTEGER),
    sum(e.num_of_question)
FROM
     examfield AS e
INNER JOIN fieldresult AS f
    ON e.id = f.examfield_id
INNER JOIN result r
    ON f.result_id = r.id
WHERE upload_time > now() - interval '1 week' AND userrole_id = %s AND r.is_active = true AND r.exam_id is not null
GROUP BY
    e.field_name;
"""


GET_FIELD_RESULTS_LAST_MONTH = """
SELECT
    e.field_name,
    count(e.field_name),
    sum(f.corrects::INTEGER),
    sum(f.wrongs::INTEGER),
    sum(f.unanswereds::INTEGER),
    sum(e.num_of_question)
FROM
     examfield AS e
INNER JOIN fieldresult AS f
    ON e.id = f.examfield_id
INNER JOIN result r
    ON f.result_id = r.id
WHERE upload_time > now() - interval '1 month' AND userrole_id = %s AND r.is_active = true AND r.exam_id is not null
GROUP BY
    e.field_name;
"""

GET_PUBLISHER_DETAIL_INFO_STATEMENT = """
SELECT
    p.first_name,
    p.email,
    p.reg_date,
    count(DISTINCT e.id) as exam_count,
    count(DISTINCT a.id) as sheet_count,
    sum(r.corrects) as corrects,
    sum(r.corrects) + sum(r.wrongs) + sum(r.unanswereds) as questions
FROM
    userrole AS p
FULL JOIN exam AS e
    ON e.publisher_id = p.id
FULL JOIN answersheet AS a
    ON e.id = a.exam_id
FULL JOIN result AS r
    ON a.id = r.sheet_id
WHERE p.id = %s
GROUP BY
         p.first_name,
         p.email,
         p.reg_date;
"""

FIELD_RESULTS_ADDED_THIS_MONTH_BUT_NOT_LAST_WEEK = """
SELECT
    e.field_name,
    count(e.field_name),
    sum(f.corrects::INTEGER),
    sum(f.wrongs::INTEGER),
    sum(f.unanswereds::INTEGER),
    sum(e.num_of_question)
FROM
     examfield AS e
INNER JOIN fieldresult AS f
    ON e.id = f.examfield_id
INNER JOIN result r
    ON f.result_id = r.id
WHERE upload_time > now() - interval '1 month' AND userrole_id = %s AND r.is_active = true AND r.exam_id is not null
GROUP BY
    e.field_name
EXCEPT
SELECT
    e.field_name,
    count(e.field_name),
    sum(f.corrects::INTEGER),
    sum(f.wrongs::INTEGER),
    sum(f.unanswereds::INTEGER),
    sum(e.num_of_question)
FROM
     examfield AS e
INNER JOIN fieldresult AS f
    ON e.id = f.examfield_id
INNER JOIN result r
    ON f.result_id = r.id
WHERE upload_time > now() - interval '1 week' AND userrole_id = %s AND r.is_active = true AND r.exam_id is not null
GROUP BY
    e.field_name;
"""

def del_db(app):
    """ Drop all tables in database. """
    with app.app_context():
        url = current_app.config['DATABASE']
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                for table in TABLE_NAMES:
                    cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")


def init_db(app, override=False):
    """ Initialize database using DDL statements."""
    if override:
        del_db(app)
    with app.app_context():
        url = current_app.config['DATABASE']
        with psycopg2.connect(url) as conn:
            with conn.cursor() as cur:
                cur.execute(DB_INITIAL_QUERY)


def register_user(first_name, last_name, email, password, is_admin=False, is_publisher=False):
    """ Register user with given information. """
    p_hash = generate_password_hash(password)
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(REGISTER_USER_STATEMENT, (
                first_name, last_name, email, p_hash, is_admin, is_publisher
            ))


def get_user_by_email(email):
    """ Get user given email address. Return None if not exists. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE email = %s", (email,))
            res = cur.fetchone()
    return res


def get_user_by_id(uid):
    """ Get user given user id. Return None if not exists. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE id = %s", (uid,))
            res = cur.fetchone()
    return res


def create_super_user(app, first_name="admin", last_name="", email=None, password=None):
    """ Create superuser with credentials given as environment variables."""
    print("Creating superuser...")
    is_admin = True
    is_publisher = False
    with app.app_context():
        if email is None:
            email = config("ADMIN_EMAIL")
        if password is None:
            password = config("ADMIN_PASSWORD")
        p_hash = generate_password_hash(password)
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
    """ Add a publisher account to system. Requires admin privileges."""
    p_hash = generate_password_hash(password)
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(REGISTER_USER_STATEMENT, (
                pub_name, "", email, p_hash, is_admin, is_publisher
            ))


def get_publishers():
    """ Fetch and return all registered publishers."""
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE is_publisher = %s ORDER BY reg_date DESC;", ('true',))
            res = cur.fetchall()
    return res


def get_exams(pub_id):
    """ Fetch and return all exams created by publisher with given id."""
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM exam WHERE publisher_id = %s ORDER BY upload_time DESC;", (pub_id,))
            res = cur.fetchall()
    return res


def create_exam_template(pub_id, title, exam_type):
    """ Create a row in exam table. Create a random code. Redirect answer fill page. """
    url = current_app.config['DATABASE']
    code = ''.join(random.choices(string.ascii_uppercase, k=10))  # 10 chars random key
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(CREATE_EXAM_TEMPLATE_STATEMENT, (
                    pub_id, title, code, exam_type, False
                ))
            except psycopg2.errors.UniqueViolation:  # if code exists
                code = ''.join(random.choices(string.ascii_uppercase, k=10))  # 10 chars random key
                cur.execute(CREATE_EXAM_TEMPLATE_STATEMENT, (
                    pub_id, title, code, exam_type, False
                ))
            cur.execute("SELECT * FROM exam WHERE code = %s;", (code,))  # select created exam
            res = cur.fetchone()  # fetch it
    return res[0]  # return exam id


def create_examfield(exam_id, field_name, num_of_q, answer_list):
    """ create exam field to fill correct answers of exam with given id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_EXAMFIELD_TEMPLATE_STATEMENT, (
                exam_id, field_name, num_of_q, answer_list
            ))


def activate_exam(exam_id):
    """ activate exam with given exam_id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(ACTIVATE_EXAM_STATEMENT, (exam_id,))


def deactivate_exam(exam_id):
    """ deactivate exam with given exam_id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(DEACTIVATE_EXAM_STATEMENT, (exam_id,))


def activate_result(result_id):
    """ activate result with given result_id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE result SET is_active = true WHERE id=%s", (result_id,))


def deactivate_result(result_id):
    """ deactivate result with given result_id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE result SET is_active = false WHERE id=%s", (result_id,))


def get_result_by_id(student_id, result_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT (is_active) FROM result WHERE id = %s AND userrole_id = %s;", (result_id, student_id))
            res = cur.fetchone()
    return res


def get_publisher_of_exam(exam_id):
    """ return the publisher information of exam with given exam_id """
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
    """ delete publisher account from system with all its exams and examfields. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(DELETE_USER_BY_ID_STATEMENT, (pub_id, ))


def get_results_of_student(student_id):
    """ get results of the student with given id """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM result WHERE userrole_id = %s ORDER BY upload_time DESC;", (student_id, ))
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


def create_field_result(examfield_id, result_id, corrects, wrongs, unanswereds):
    statement = """
    INSERT INTO
        fieldresult (examfield_id, result_id, corrects, wrongs, unanswereds)
    VALUES 
        (%s, %s, %s, %s, %s);
    """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(statement, (examfield_id, result_id, corrects, wrongs, unanswereds))


def calculate_result(user_id, sheet_id, exam_id):
    """ calculate the correct, worng and unanswered question comparing answer sheet and exam with
     given ids. create a database entry in result table. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            # create result in database
            cur.execute(CREATE_RESULT_STATEMENT, (user_id, exam_id, sheet_id))
            conn.commit()

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

                create_field_result(exam_field[0], result[0], field_corrects, field_wrongs, field_unanswereds)

                total_corrects += field_corrects
                total_wrongs += field_wrongs
                total_unanswereds += field_unanswereds

            net = total_corrects - 0.25*total_wrongs
            cur.execute(UPDATE_RESULT_STATEMENT, (total_corrects, total_wrongs, total_unanswereds, net, sheet_id))


def get_joined_result_data(student_id):
    """ get combined result and exam information to display on student dashboard. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(JOIN_USER_RESULT_EXAM, (student_id, ))
            res = cur.fetchall()
    return res


def get_field_results_of_student(student_id):
    """ get combined field result information to display on student lecture page. """
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:

            cur.execute(GET_FIELD_RESULTS_LAST_WEEK, (student_id,))
            last_week = cur.fetchall()

            cur.execute(GET_FIELD_RESULTS_LAST_MONTH, (student_id,))
            last_month = cur.fetchall()

            cur.execute(GET_FIELD_RESULTS_STATEMENT, (student_id,))
            general = cur.fetchone()
    print(last_week, last_month, general)
    return last_week, last_month, general


def get_publisher_by_id(publisher_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE is_publisher = %s AND id=%s;", ('true', publisher_id))
            res = cur.fetchone()
    return res


def get_profile_info_of_publisher(publisher_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(GET_PUBLISHER_DETAIL_INFO_STATEMENT, (publisher_id, ))
            res = cur.fetchone()
    return res


def get_exam_by_id(exam_id):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM exam WHERE id = %s", (exam_id,))
            res = cur.fetchone()
    return res


def delete_exam_from_database(exam_id):
    """ delete exam from system with all its examexamfields. """

    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM exam WHERE id = %s ;", (exam_id, ))


def delete_result_from_database(result_id):
    """ delete exam from system with all its examexamfields. """

    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM result WHERE id = %s ;", (result_id, ))
