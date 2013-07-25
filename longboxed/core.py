# -*- coding: utf-8 -*-
"""
    longboxed.core
    ~~~~~~~~~~~~~

    core module
"""

from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
# from flask.ext.mongokit import MongoKit
from flask.ext.mongoengine import MongoEngine

#: Flask-Bootstrap extension instance
bootstrap = Bootstrap()

#: Flask-Login extension instance
login_manager = LoginManager()

#: Flask-MongoKit extension instance
db = MongoEngine()


class LongboxedError(Exception):
    """Base application error class"""

    def __init__(self, msg):
        self.msg = msg

class LongboxedFormError(Exception):
    """Raise when an error processing a form occurs."""

    def __init__(self, errors=None):
        self.errors = errors

class Service(object):
    __model__ = None