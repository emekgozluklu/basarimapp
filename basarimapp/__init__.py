from flask import Flask
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

    # a simple page that says hello
    @app.route('/')
    def hello():
        return 'Index page will be here!!'

    return app
