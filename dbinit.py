import psycopg2
from decouple import config
import os

fn = os.path.join(".", "db_structure.sql")
DB_INITIAL_QUERY = open(fn, "r").read()
TABLE_NAMES = ["USERROLE", "EXAM", "EXAMFIELD", "RESULT", "FIELDRESULT", "ANSWERSHEET"]


def initialize(url):
    with psycopg2.connect(url) as connection:
        cursor = connection.cursor()
        cursor.execute(DB_INITIAL_QUERY)
        cursor.close()


def deinit(url):
    with psycopg2.connect(url) as connection:
        cursor = connection.cursor()
        for table_name in TABLE_NAMES:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        cursor.close()


if __name__ == "__main__":
    url = config("DATABASE_URL")
    # deinit(url)
    initialize(url)
