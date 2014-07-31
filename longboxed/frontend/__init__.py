# -*- coding: utf-8 -*-
"""
    longboxed.frontend
    ~~~~~~~~~~~~~~~~~~

    launchpad frontend application package
"""

from flask import render_template
# from flask.ext.debugtoolbar import DebugToolbarExtension
from functools import wraps

from .. import factory
from ..helpers import pretty_date
from . import admin


def create_app(config_name):
    """Returns the Longboxed dashboard application instance

    :param settings_override: dictionary of settings to overide
    """
    app = factory.create_app(__name__, __path__, config_name)
    
    #: Register custom Jinja2 filters
    app.jinja_env.filters['pretty_date'] = pretty_date

    #: Init assets
    # assets.init_app(app)
    #: Flask-Admin
    admin.init_app(app)

    #: Flask-DebugToolbar
    # DebugToolbarExtension(app)

    #: Register custom error handlers
    if not app.debug:
        for e in [500, 404]:
            app.errorhandler(e)(handle_error)

    return app


def handle_error(e):
    return render_template('errors/%s.html' % e.code), e.code


def route(bp, *args, **kwargs):
    """Route decorator for use in blueprints"""
    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return f

    return decorator
