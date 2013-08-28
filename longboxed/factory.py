# -*- coding: utf-8 -*-
"""
    longboxed.factory
    ~~~~~~~~~~~~~~~~

    longboxed factory module
"""
import os

from celery import Celery
from flask import Flask
from flask.ext.security import SQLAlchemyUserDatastore

from .core import bootstrap, db, mail, security
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from .models import User, Role


def create_app(package_name, package_path, settings_override=None, register_security_blueprint=True):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Longboxed platform.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    """
    app = Flask(package_name, instance_relative_config=True)

    app.config.from_object('longboxed.settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_object(settings_override)

    bootstrap.init_app(app)
    db.init_app(app)
    # login_manager.init_app(app)

    mail.init_app(app)

    #: Setup Flask-Security
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role),
                      register_blueprint=register_security_blueprint)



    # register_models(db, package_name, package_path)
    register_blueprints(app, package_name, package_path)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    return app


def create_celery_app(app=None):
    app = app or create_app('longboxed', os.path.dirname(__file__))
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery