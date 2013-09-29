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
from sqlalchemy_imageattach.context import push_store_context, pop_store_context

from . import signals
from .core import bootstrap, db, mail, security, store
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware
from .models import User, Role


def create_app(package_name, package_path, settings_override=None, debug_override=None, register_security_blueprint=True):
    """Returns a :class:`Flask` application instance configured with common
    functionality for the Longboxed platform.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    :param debug_overide: :class:`Bool` value that overrides the debug settings
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

    # Register all blueprints
    register_blueprints(app, package_name, package_path)

    # Register all signal handlers
    signals.init_app(app)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)
    app.wsgi_app = store.wsgi_middleware(app.wsgi_app)

    @app.before_request
    def start_implicit_store_context():
        push_store_context(store)

    @app.teardown_request
    def stop_implicit_store_context(exception=None):
        try:
            pop_store_context()
        except IndexError:
            pass

    #: Setup Logging if not debug
    setup_logging()

    return app


def create_celery_app(app=None):
    """
    Factory method that to place a Celery instance in the context
    of a Flask application

    :param app: :class:`Flask` application instance
    """
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

    :param default_path: Path to json log configuration file
    :param default_level: Level to set the logger at. Default to INFO level
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
    """
    Filter function. Used in a logging json configuration file to allow a handler to 
    log only its own specific log level.
    """

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