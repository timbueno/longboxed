# -*- coding: utf-8 -*-
"""
    longboxed.frontend.authorization
    ~~~~~~~~~~~~~~~~~~

    Authorization blueprints
"""

from flask import Blueprint

from . import route

bp = Blueprint('authorization', __name__)

@route(bp, '/login')
def login():
    return 5