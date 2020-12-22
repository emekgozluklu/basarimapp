from flask import Flask
from .database_init import init_db
import basarimapp.views
import os


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])

    if test_config is not None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config_test.py', silent=True)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # init_db()  # restarts database

    # add url rules
    app.add_url_rule("/", view_func=views.index)

    return app
