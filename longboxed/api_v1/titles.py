# -*- coding: utf-8 -*-
"""
    longboxed.api.titles
    ~~~~~~~~~~~~~~~~~~~~

    Title endpoints
"""
from datetime import datetime

from flask import Blueprint, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from ..helpers import current_wednesday, next_wednesday, after_wednesday
from ..models import Title, Issue
from .errors import bad_request
from . import route


bp = Blueprint('titles', __name__, url_prefix='/titles')


@route(bp, '/')
def get_titles():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    pagination = Title.query.paginate(page, per_page=count, error_out=False)
    titles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'titles': [title.to_json() for title in titles],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/<int:id>')
def get_title(id):
    title = Title.query.get_or_404(id)
    return jsonify({
        'title': title.to_json()
    })


@route(bp, '/<int:id>/issues/')
def get_issues_for_title(id):
    title = Title.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)

    # Set the maximum date to search for issues (This week or next week)
    date = next_wednesday() if after_wednesday(datetime.today().date()) else current_wednesday()

    pagination = Issue.query.filter(Issue.title==title, Issue.on_sale_date <= date) \
        .order_by(Issue.on_sale_date.desc()) \
        .paginate(page, per_page=count, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'title': title.name,
        'issues': [issue.to_json() for issue in issues],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
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
        res = Title.query.filter(Title.name.ilike(searchstring)).\
                         order_by(Title.num_subscribers.desc()).\
                         limit(20).\
                         all()
        return jsonify({
                'query': fragment,
                'suggestions': [r.to_json() for r in res],
        })
    except NoResultFound:
        return jsonify({'query': fragment, 'suggestions':[]})
