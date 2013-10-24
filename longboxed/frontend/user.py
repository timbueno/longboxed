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
    twitter = current_app.social.twitter
    # twitter.get_api()
    # print twitter.get_connection()
    return render_template(
        'profile.html',
        twitter_conn=twitter.get_connection(),
        google_conn=current_app.social.google.get_connection(),
        facebook_conn=current_app.social.facebook.get_connection()
    )