# -*- coding: utf-8 -*-
"""
    longboxed.api.titles
    ~~~~~~~~~~~~~~~~~~~~

    Title endpoints
"""
from datetime import datetime

from flask import current_app, Blueprint, jsonify, request
from sqlalchemy.orm.exc import NoResultFound

from ..core import cache
from ..helpers import (current_wednesday, next_wednesday, after_wednesday,
                       make_cache_key)
from ..models import Title, Issue, Publisher
from .errors import bad_request
from . import route


bp = Blueprint('titles', __name__, url_prefix='/titles')


@route(bp, '/test/<int:id>')
@cache.cached(timeout=30, key_prefix=make_cache_key)
def test(id):
    print 'NOT CACHE'
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))
    return str(a + b + id)


@route(bp, '/')
@cache.cached(timeout=300, key_prefix=make_cache_key)
def get_titles():
    print 'NOT CACHE'
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    disabled_pubs = current_app.config.get('DISABLED_PUBS', [])
    #pagination = Title.query.order_by(Title.name)\
    #                        .paginate(page, per_page=count, error_out=False)
    pagination = Title.query.join(Title.publisher)\
                            .filter(Publisher.name.notin_(disabled_pubs))\
                            .order_by(Title.name)\
                            .paginate(page, per_page=count, error_out=False)
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
    if title.publisher.name in current_app.config.get('DISABLED_PUBS', []):
        return bad_request('Titles not available from this publisher')
    return jsonify({
        'title': title.to_json()
    })


@route(bp, '/<int:id>/issues/')
def get_issues_for_title(id):
    title = Title.query.get_or_404(id)
    if title.publisher.name in current_app.config.get('DISABLED_PUBS', []):
        return bad_request('Titles not available from this publisher')
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)

    # Set the maximum date to search for issues (This week or next week)
    if after_wednesday(datetime.today().date()):
        date = next_wednesday()
    else:
        date = current_wednesday()

    pagination = Issue.query.filter(
                                Issue.title==title,
                                Issue.is_parent==True,
                                Issue.on_sale_date <= date,
                                Issue.on_sale_date != None)\
                            .order_by(Issue.on_sale_date.desc())\
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
    disabled_pubs = current_app.config.get('DISABLED_PUBS', [])
    fragment = request.args.get('query')
    keywords = fragment.split()
    searchstring = '%%'.join(keywords)
    searchstring = '%%%s%%' % (searchstring)
    try:
        #res = Title.query.filter(Title.name.ilike(searchstring))\
        #                 .order_by(Title.num_subscribers.desc())\
        #                 .limit(20)\
        #                 .all()
        res = Title.query.filter(Title.name.ilike(searchstring))\
                         .join(Title.publisher)\
                         .filter(Publisher.name.notin_(disabled_pubs))\
                         .order_by(Title.num_subscribers.desc())\
                         .limit(10)\
                         .all()
        return jsonify({
                'query': fragment,
                'suggestions': [r.to_json() for r in res],
        })
    except NoResultFound:
        return jsonify({'query': fragment, 'suggestions':[]})
