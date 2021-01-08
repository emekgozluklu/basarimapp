from flask import render_template, redirect, url_for
from decouple import config
import psycopg2


def index():
    return render_template("index.html")
