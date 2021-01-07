from decouple import config
from flask import Flask
from basarimapp import views


def create_app(cfg="DEV"):
    app = Flask(__name__)

    app.config['DEBUG'] = True
    app.config['CSRF_ENABLED'] = True
    app.config['SECRET_KEY'] = config('SECRET_KEY')

    if cfg == "DEV":
        app.config['DATABASE'] = config('DATABASE_URL')

    elif cfg == "TESTING":
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DATABASE'] = config('TEST_DATABASE_URL')

    # with app.app_context():
    #     init_db()  # restarts database

    # add url rules
    app.add_url_rule("/", view_func=views.index)
    app.add_url_rule("/login", view_func=views.login, methods=["GET", "POST"])
    app.add_url_rule("/register", view_func=views.register, methods=["GET", "POST"])

    return app
