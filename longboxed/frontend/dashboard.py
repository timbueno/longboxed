# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""
from flask import Blueprint, g, render_template
from flask.ext.security import current_user

from . import route
from ..helpers import current_wednesday
from ..services import comics as _comics


bp = Blueprint('dashboard', __name__)

@bp.before_app_request
def before_request():
    if not current_user.is_anonymous():
        g.user = current_user
    else:
        g.user = None


@route(bp, '/test')
def test():
    return render_template('layouts/longboxed_base.html')


@route(bp, '/')
def index():
    issues = _comics.issues.__model__.query.filter(_comics.issues.__model__.on_sale_date == current_wednesday(), _comics.issues.__model__.is_parent == True).order_by(_comics.issues.__model__.popularity).limit(4)
    return render_template('index.html', issues=issues)