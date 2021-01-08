from flask import current_app
from basarimapp import create_app
import psycopg2
import os

curdir = os.getcwd()
fn = os.path.join(curdir, "db_structure.sql")
DB_INITIAL_QUERY = open(fn, "r").read()
TABLE_NAMES = ["USERROLE", "EXAM", "EXAMFIELD", "RESULT", "FIELDRESULT", "ANSWERSHEET"]

REGISTER_USER_STATEMENT = """
INSERT INTO userrole (first_name, last_name, email, password_hash, is_admin, is_publisher)
VALUES (%s, %s, %s, %s, %s, %s);
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


def register_user(first_name, last_name, email, p_hash, is_admin=False, is_publisher=False):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute(REGISTER_USER_STATEMENT, (
                first_name, last_name, email, p_hash, is_admin, is_publisher
            ))


def get_user(email):
    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole WHERE email = %s", (email,))
            res = cur.fetchone()
    return res


if __name__ == "__main__":
    print("Reinitializing database.")
    app = create_app()
    init_db(app, override=True)
    print("Done!")
