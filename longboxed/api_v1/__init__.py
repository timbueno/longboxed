# -*- coding: utf-8 -*-
"""
    longboxed.api
    ~~~~~~~~~~~~~

    longboxed api application package
"""
from functools import wraps

from flask import jsonify

from ..core import LongboxedError, LongboxedFormError
from .. import factory

def create_app(config_name, register_security_blueprint=False):
    """Returns the Longboxed API application instance"""
    app = factory.create_app(__name__, __path__, config_name,
                             register_security_blueprint=register_security_blueprint)

    # Register custom error handlers
    app.errorhandler(LongboxedError)(on_longboxed_error)
    app.errorhandler(LongboxedFormError)(on_longboxed_form_error)
    app.errorhandler(404)(on_404)

    return app


def route(bp, *args, **kwargs):
    kwargs.setdefault('strict_slashes', True)

    def decorator(f):
        @bp.route(*args, **kwargs)
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return f

    return decorator


def on_longboxed_error(e):
    return jsonify(dict(error=e.msg)), 400


def on_longboxed_form_error(e):
    return jsonify(dict(errors=e.errors)), 400


def on_404(e):
    return jsonify(dict(error='Not found')), 404