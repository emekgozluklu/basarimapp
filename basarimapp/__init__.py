from decouple import config
from flask import Flask
from basarimapp import views, auth, admin
from basarimapp.dbmanager import init_db, create_super_user


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

    # init_db(app, override=True)  # restarts database

    create_super_user(app)

    # add url rules
    app.add_url_rule("/", view_func=views.index)

    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)

    return app
