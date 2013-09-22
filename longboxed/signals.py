from flask.ext.security.signals import user_registered
from werkzeug.local import LocalProxy

from .core import db


def user_registered_signal_handler(app, user, confirm_token):
    """Executed imediately after user registers a new account.
    Adds a default 'user' role to the new user
    """
    _security_datastore = LocalProxy(lambda: app.extensions['security'].datastore)
    default_role = _security_datastore.find_role('user')
    _security_datastore.add_role_to_user(user, default_role)
    db.session.commit()


# Run this function from the app factory to register signal handlers
def init_app(app):
    user_registered.connect_via(app)(user_registered_signal_handler)