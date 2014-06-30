# -*- coding: utf-8 -*-
"""
    longboxed.api.users
    ~~~~~~~~~~~~~~~~~~~~

    Users endpoints
"""
from flask import Blueprint, g, jsonify

# from ..services import users
from .authentication import auth
from . import route


bp = Blueprint('users', __name__, url_prefix='/users')


@route(bp, '/login')
@auth.login_required
def login():
    return jsonify(g.current_user.to_json())
