# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""

from flask import Blueprint, render_template, g
from flask.ext.login import (current_user, login_required,
                            login_user, logout_user, confirm_login,
                            fresh_login_required)

from . import route

bp = Blueprint('dashboard', __name__)

# @route(bp, '/')
# def index():
#     """Returns to the dashboard interface."""
#     return render_template('dashboard.html')

@route(bp, '/')
def index():
    if not current_user.is_anonymous():
        pass
    return 'cool'
