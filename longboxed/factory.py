# -*- coding: utf-8 -*-
"""
    longboxed.factory
    ~~~~~~~~~~~~~~~~

    longboxed factory module
"""
from flask import Flask

from .core import bootstrap, db, login_manager
from .helpers import register_blueprints
from .middleware import HTTPMethodOverrideMiddleware


def create_app(package_name, package_path, settings_override=None):
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
    login_manager.init_app(app)

    # register_models(db, package_name, package_path)
    register_blueprints(app, package_name, package_path)

    app.wsgi_app = HTTPMethodOverrideMiddleware(app.wsgi_app)

    return app