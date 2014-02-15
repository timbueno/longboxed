# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import current_app, Blueprint, redirect, render_template, url_for
from flask.ext.security import current_user, login_required

from . import route
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
    bundles = current_user.bundles.order_by(Bundle.release_date.desc()).paginate(page=page, per_page=3)
    return render_template('bundles.html', bundles=bundles)