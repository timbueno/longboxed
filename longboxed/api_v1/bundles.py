# -*- coding: utf-8 -*-
"""
    longboxed.api.bundles
    ~~~~~~~~~~~~~~~~~~~~

    Bundle endpoints
"""

from flask import Blueprint, g, jsonify

from . import route
from .authentication import auth
from ..services import bundle as _bundles


bp = Blueprint('bundles', __name__, url_prefix='/bundles')


@route(bp, '/')
@auth.login_required
def get_all_bundles():
    bundles = g.current_user.bundles
    return jsonify({
        'bundles': [bundle.to_json() for bundle in bundles]
    })


@route(bp, '/<int:id>')
@auth.login_required
def get_bundle(id):
    bundle = _bundles.get(id)
    return jsonify(bundle.to_json())