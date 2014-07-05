# -*- coding: utf-8 -*-
"""
    longboxed.api.titles
    ~~~~~~~~~~~~~~~~~~~~

    Title endpoints
"""

from flask import Blueprint, jsonify, request, url_for
from sqlalchemy.orm.exc import NoResultFound

from ..helpers import current_wednesday
from ..services import comics
from .errors import bad_request
from . import route


bp = Blueprint('titles', __name__, url_prefix='/titles')


@route(bp, '/')
def get_titles():
    page = request.args.get('page', 1, type=int)
    pagination = comics.titles.__model__.query.paginate(page, per_page=20, error_out=False)
    titles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_titles', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_titles', page=page+1, _external=True)
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
    from ..comics.models import Issue
    title = comics.titles.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = Issue.query.filter(Issue.title==title, Issue.on_sale_date <= current_wednesday()) \
        .order_by(Issue.on_sale_date.desc()) \
        .paginate(page, per_page=5, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('.get_issues_for_title', id=id, page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('.get_issues_for_title', id=id, page=page+1, _external=True)
    return jsonify({
        'title': title.name,
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'issues': [issue.to_json() for issue in issues]
    })


@route(bp, '/autocomplete/', methods=['GET'])
def autocomplete():
    if 'query' not in request.args.keys():
        return bad_request('Must submit a \'query\' parameter!')
    fragment = request.args.get('query')
    keywords = fragment.split()
    searchstring = '%%'.join(keywords)
    searchstring = '%%%s%%' % (searchstring)
    try:
        from ..comics.models import Title
        res = Title.query.filter(Title.name.ilike(searchstring)).\
                         order_by(Title.num_subscribers.desc()).\
                         limit(10).\
                         all()
        return jsonify({
                'query': fragment,
                'suggestions': [r.to_json() for r in res],
        })
    except NoResultFound:
        return jsonify({'query': fragment, 'suggestions':[]})
