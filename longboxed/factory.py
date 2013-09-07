# -*- coding: utf-8 -*-
"""
    longboxed.factory
    ~~~~~~~~~~~~~~~~

    longboxed factory module
"""
import os
import json

import logging
import logging.config

from celery import Celery
from flask import Flask
from flask.ext.security import SQLAlchemyUserDatastore

from .core import bootstrap, db, mail, security
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from .models import User, Role


def create_app(package_name, package_path, settings_override=None, debug_override=None, register_security_blueprint=True):
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
    if debug_override is not None:
        app.debug = debug_override

    #: Setup Flask Extentions
    bootstrap.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    #: Setup Flask-Security
    security.init_app(app, SQLAlchemyUserDatastore(db, User, Role),
                      register_blueprint=register_security_blueprint)

    # register_models(db, package_name, package_path)
    register_blueprints(app, package_name, package_path)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    #: Setup Logging if not debug
    setup_logging()

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


def setup_logging(default_path='longboxed/logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.loads(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    return


class LogOnlyLevel(object):
    def __init__(self, level):
        if level == 'DEBUG':
            level = logging.DEBUG
        elif level == 'INFO':
            level = logging.INFO
        elif level == 'ERROR':
            level = logging.ERROR
        else:
            print 'Something is wrong with your filter...'
            level = None
        self.__level = level

    def filter(self, logRecord):
        return logRecord.levelno <= self.__level