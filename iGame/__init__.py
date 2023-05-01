import os

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_modals import Modal
from config import config

bootstrap = Bootstrap5()
modal = Modal()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.index'


def create_app(config_name):
    # create and configure the app
    app = Flask('igame', template_folder='igame/templates')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    login_manager.init_app(app)
    modal.init_app(app)
    db.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app