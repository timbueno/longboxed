# -*- coding: utf-8 -*-
"""
    longboxed.frontend.users
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    User blueprints
"""
from flask import Blueprint, redirect, render_template, url_for
from flask.ext.security import current_user, login_required

from . import route
from ..models import Bundle


bp = Blueprint('users', __name__)


@route(bp, '/bundles')
@login_required
def bundles_redirect():
    return redirect(url_for('users.bundles', page=1))

@route(bp, '/bundles/<int:page>')
@login_required
def bundles(page):
    bundles = current_user.bundles.order_by(Bundle.release_date.desc()).paginate(page=page, per_page=3)
    return render_template('bundles.html', bundles=bundles)

