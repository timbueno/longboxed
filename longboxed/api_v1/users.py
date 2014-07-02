# -*- coding: utf-8 -*-
"""
    longboxed.api.users
    ~~~~~~~~~~~~~~~~~~~~

    Users endpoints
"""
from flask import Blueprint, g, jsonify, request, url_for

from ..services import comics, users
from .authentication import auth
from .errors import bad_request, forbidden
from . import route


bp = Blueprint('users', __name__, url_prefix='/users')


@route(bp, '/login')
@auth.login_required
def login():
    return jsonify(g.current_user.to_json())


@route(bp, '/<int:id>/pull_list/', methods=['GET'])
@auth.login_required
def get_user_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/pull_list/', methods=['POST'])
@auth.login_required
def add_title_to_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    title_id = request.args.get('title_id', type=int)
    if title_id:
        title_id = int(title_id)
        title = comics.titles.get_or_404(title_id)
    else:
        return bad_request('title_id: attribute not found')
    if title not in g.current_user.pull_list:
        g.current_user.pull_list.append(title)
        g.current_user = users.save(g.current_user)
    else:
        return bad_request('Title is already on users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/pull_list/', methods=['DELETE'])
@auth.login_required
def remove_title_from_pull_list(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    title_id = request.args.get('title_id', type=int)
    if title_id:
        title_id = int(title_id)
        title = comics.titles.get_or_404(title_id)
    else:
        return bad_request('title_id: attribute not found')
    if title in g.current_user.pull_list:
        g.current_user.pull_list.remove(title)
        g.current_user = users.save(g.current_user)
    else:
        return bad_request('Title is not on the users pull list')
    return jsonify({
        'user': g.current_user.email,
        'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })


@route(bp, '/<int:id>/bundles/', methods=['GET'])
@auth.login_required
def get_user_bundles(id):
    if id != g.current_user.id:
        return forbidden('You do not have permission to access this users pull list')
    page = request.args.get('page', 1, type=int)
    pagination = g.current_user.bundles.paginate(page, per_page=5, error_out=False)
    bundles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_user_bundles', id=g.current_user.id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_user_bundles', id=g.current_user.id, page=page+1, _external=True)
    return jsonify({
        'prev': prev,
        'next': next,
        'bundles': [bundle.to_json() for bundle in bundles]
    })