from configparser import ConfigParser
from flask import current_app
import psycopg2
import os


curdir = os.getcwd()
fn = os.path.join(curdir, "db_structure.sql")
ini_file_path = os.path.join(curdir, "database.ini")
DB_INITIAL_QUERY = open(fn, "r").read()
TABLE_NAMES = ["USERROLE", "EXAM", "EXAMFIELD", "RESULT", "FIELDRESULT", "ANSWERSHEET"]


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


class DBManager:

    def __init__(self):
        self.url = current_app.config['DATABASE']
        self.conn = psycopg2.connect(self.url)

    def get_database(self):
        if 'db' not in g:
            g.db = dbapi2.connect(self.url)
        return g.db

    def execute_command(self, command):
        cur = self.conn.cursor()
        cur.execute(command)
        res = cur.fetchall()
        cur.close()
        return res

    def select_all(self, table_name):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table_name};")
        res = cur.fetchall()
        cur.close()
        return res

    def select(self, table_name, condition):
        cur = self.conn.cursor()
        cur.execute(f"SELECT * FROM {table_name} WHERE {condition};")
        res = cur.fetchall()
        cur.close()
        return res

    def insert(self, table_name, values):
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO {table_name} VALUES {values};")
        cur.close()

    @staticmethod
    def close_db():
        db = g.pop('db', None)

        if db is not None:
            db.close()


if __name__ == "__main__":
    # del_db()
    init_db()
