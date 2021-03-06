# -*- coding: utf-8 -*-
"""
    longboxed.api.authentication
    ~~~~~~~~~~~~~

    longboxed api authentication
"""

from flask import g
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.security import AnonymousUser
from flask.ext.security.utils import verify_password as check_password

from .errors import unauthorized
from ..models import User


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password):
    if email == '':
        g.current_user = AnonymousUser()
        return True
    user = User.query.filter(User.email.ilike(email)).first()
    if not user:
        return False
    g.current_user = user
    password_success = check_password(password, user.password)
    if password_success:
        g.current_user.ping()
    return password_success


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

