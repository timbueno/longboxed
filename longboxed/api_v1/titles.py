# -*- coding: utf-8 -*-
"""
    longboxed.api.titles
    ~~~~~~~~~~~~~~~~~~~~

    Title endpoints
"""

from flask import Blueprint, jsonify, request, url_for

from ..services import comics
from . import route


bp = Blueprint('titles', __name__, url_prefix='/titles')


@route(bp, '/')
def titles():
    page = request.args.get('page', 1, type=int)
    pagination = comics.titles.__model__.query.paginate(page, per_page=20, error_out=False)
    titles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.titles', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.titles', page=page+1, _external=True)
    return jsonify({
        'titles': [title.to_json() for title in titles],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@route(bp, '/<int:id>')
def get_title(id):
    title = comics.titles.get(id)
    return jsonify(title.to_json())


@route(bp, '/<int:id>/issues/')
def get_issues_for_title(id):
    title = comics.titles.get(id)
    return jsonify({
        'title': title.name,
        'issues': [issue.to_json() for issue in title.issues]
    })