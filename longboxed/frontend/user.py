# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import current_app, Blueprint, render_template

from . import route

bp = Blueprint('users', __name__)

@route(bp, '/profile', methods=['GET', 'POST', 'DELETE'])
def profile():
    return render_template(
        'profile.html',
        google_conn=current_app.social.google.get_connection()
    )