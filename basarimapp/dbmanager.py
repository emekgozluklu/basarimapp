from flask import current_app
from werkzeug.security import generate_password_hash
from decouple import config
import psycopg2
import os
import string
import random

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


if __name__ == "__main__":
    print("Reinitializing database.")
    from basarimapp import create_app
    a = create_app()
    init_db(a, override=True)
    print("Done!")
