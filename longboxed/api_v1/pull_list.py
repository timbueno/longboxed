# -*- coding: utf-8 -*-
"""
    longboxed.api.pull_list
    ~~~~~~~~~~~~~~~~~~~~

    Pull List endpoints
"""

from flask import Blueprint, g, jsonify, request

from . import route
from .authentication import auth
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
    print 'IN THE HANDLER'
    title_id = request.args.get('id', type=int)
    print title_id
    print request.args
    title = comics.titles.get_or_404(title_id)
    g.current_user.append(title)
    users.save(g.current_user)
    return jsonify({
            'user': g.current_user.email,
            'pull_list': [title.to_json() for title in g.current_user.pull_list]
    })