# -*- coding: utf-8 -*-
"""
    longboxed.api.pull_list
    ~~~~~~~~~~~~~~~~~~~~

    Pull List endpoints
"""

from flask import Blueprint, g, jsonify, request

from . import route
from .authentication import auth
from .errors import bad_request
from ..services import users, comics


bp = Blueprint('pull_list', __name__, url_prefix='/pull_list')


@route(bp, '/')
@auth.login_required
def get_pull_list():
    return jsonify({
            'user': g.current_user.email,
            'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })


@route(bp, '/', methods=['POST'])
@auth.login_required
def add_title_to_pull_list():
    title_id = request.json.get('title_id')
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