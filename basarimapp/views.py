from flask import render_template, redirect, url_for
from decouple import config
import psycopg2


def index():
    url = config('DATABASE_URL')
    with psycopg2.connect(url) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM userrole;")
            rows = cur.fetchall()
    print(rows)
    return render_template("index.html")
