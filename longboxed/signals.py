# -*- coding: utf-8 -*-
"""
    longboxed.signals
    ~~~~~~~~~~~~~~~~~

    longboxed signals module

"""

from flask.ext.security.signals import user_registered
from werkzeug.local import LocalProxy

from .core import db
from .models import Bundle
from .helpers import current_wednesday, next_wednesday, two_wednesdays


def user_registered_signal_handler(app, user, confirm_token):
    """Executed imediately after user registers a new account.
    Adds a default 'user' role to the new user

    :param app: Flask application object
    :param user: Newly registered Flask-Login User object
    :param confirm_token: Users confirm token
    """
    _security_datastore = LocalProxy(
            lambda: app.extensions['security'].datastore)
    default_role = _security_datastore.find_role('user')
    _security_datastore.add_role_to_user(user, default_role)
    db.session.commit()
    Bundle.refresh_user_bundle(user, current_wednesday())
    Bundle.refresh_user_bundle(user, next_wednesday())
    Bundle.refresh_user_bundle(user, two_wednesdays())


def init_app(app):
    """
    Registers signal handlers with flask application

    :param app: Flask application object
    """
    user_registered.connect_via(app)(user_registered_signal_handler)
