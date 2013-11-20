# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import current_app, Blueprint, redirect, render_template, url_for
from flask.ext.security import current_user, login_required

from . import route
# from ..services import comics as _comics
# from ..services import bundle as _bundles
from ..helpers import current_wednesday, refresh_bundle
from ..models import Bundle

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


@route(bp, '/bundles')
@login_required
def bundles_redirect():
    return redirect(url_for('users.bundles', page=1))

@route(bp, '/bundles/<int:page>')
@login_required
def bundles(page):
    # bundle = list(_comics.issues.__model__.query.filter().limit(20))
    # bundle = refresh_bundle(current_user, current_wednesday())
    # bundles = current_user.bundles.order_by(Bundle.release_date.desc()).limit(5)
    bundles = current_user.bundles.order_by(Bundle.release_date.desc()).paginate(page=page, per_page=3)
    return render_template('bundles.html', bundles=bundles)