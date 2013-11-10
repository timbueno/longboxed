# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import current_app, Blueprint, render_template

from . import route

bp = Blueprint('users', __name__)

@route(bp, '/social', methods=['GET', 'POST', 'DELETE'])
def social():
    return render_template(
        'social.html',
        twitter_conn=current_app.social.twitter.get_connection(),
        google_conn=current_app.social.google.get_connection(),
        facebook_conn=current_app.social.facebook.get_connection()
    )

@route(bp, '/social')
def profile():
    return 1