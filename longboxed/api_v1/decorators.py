# -*- coding: utf-8 -*-
"""
    longboxed.api.decorators
    ~~~~~~~~~~~~~

    longboxed api decorators
"""

from functools import wraps
from flask import g
from .errors import forbidden


def authentication_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.current_user.is_anonymous():
            return forbidden('must be authenticated')
        return f(*args, **kwargs)
    return decorated_function