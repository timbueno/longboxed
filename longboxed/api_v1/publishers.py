# -*- coding: utf-8 -*-
"""
    longboxed.api.publishers
    ~~~~~~~~~~~~~~~~~~~~

    Publisher endpoints
"""
from flask import current_app, Blueprint, jsonify, request

from ..core import cache
from ..helpers import make_cache_key
from ..models import Title, Publisher
from . import route
from .errors import bad_request


bp = Blueprint('publishers', __name__, url_prefix='/publishers')


@route(bp, '/', methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def publishers():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    disabled_pubs = current_app.config.get('DISABLED_PUBS', [])
    #pagination = Publisher.query.order_by(Publisher.name)\
    #                            .paginate(page, per_page=count, error_out=False)
    pagination = Publisher.query.filter(Publisher.name.notin_(disabled_pubs))\
                                .order_by(Publisher.name)\
                                .paginate(page, per_page=count, error_out=False)
    publishers = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'publishers': [publisher.to_json() for publisher in publishers],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/<int:id>', methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def get_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    if publisher.name in current_app.config.get('DISABLED_PUBS', []):
        return bad_request('Publisher not available')
    return jsonify({
        'publisher': publisher.to_json()
    })


@route(bp, '/<int:id>/titles/', methods=['GET'])
@cache.cached(key_prefix=make_cache_key)
def get_titles_for_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    if publisher.name in current_app.config.get('DISABLED_PUBS', []):
        return bad_request('Publisher not available')
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    pagination = publisher.titles.order_by(Title.name)\
                                 .paginate(page, per_page=count, error_out=False)
    titles = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'publisher': publisher.name,
        'titles': [title.to_json() for title in titles],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })
