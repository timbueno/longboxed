# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import current_app, Blueprint, render_template
from flask.ext.security import current_user, login_required

from . import route
# from ..services import comics as _comics
# from ..services import bundle as _bundles
from ..helpers import current_wednesday, refresh_bundle

bp = Blueprint('users', __name__)

@route(bp, '/social', methods=['GET', 'POST', 'DELETE'])
@login_required
def social():
    return render_template(
        'social.html',
        twitter_conn=current_app.social.twitter.get_connection(),
        google_conn=current_app.social.google.get_connection(),
        facebook_conn=current_app.social.facebook.get_connection()
    )

@route(bp, '/profile')
def profile():
    # bundle = list(_comics.issues.__model__.query.filter().limit(20))
    bundle = refresh_bundle(current_user, current_wednesday())
    return render_template('profile.html', bundles=current_user.bundles)