from configparser import ConfigParser
from flask import current_app
import psycopg2
import os


curdir = os.getcwd()
fn = os.path.join(curdir, "db_structure.sql")
ini_file_path = os.path.join(curdir, "database.ini")
DB_INITIAL_QUERY = open(fn, "r").read()
TABLE_NAMES = ["USERROLE", "EXAM", "EXAMFIELD", "RESULT", "FIELDRESULT", "ANSWERSHEET"]


def get_params(filename, section):
    parser = ConfigParser()
    parser.read(filename)

    db = {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            "Section {0} not found in the {1} file".format(section, filename)
        )
    return db


def del_db():

    url = current_app.config['DATABASE']
    with psycopg2.connect(url) as conn:
        cur = conn.cursor()
        for table in TABLE_NAMES:
            cur.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
    cur.close()


def init_db(override=False):

    if override:
        del_db()

    url = current_app.config['DATABASE']

    with psycopg2.connect(url) as conn:
        cur = conn.cursor()
        cur.execute(DB_INITIAL_QUERY)
    cur.close()


if __name__ == "__main__":
    # del_db()
    init_db()
