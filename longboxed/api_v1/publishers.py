# -*- coding: utf-8 -*-
"""
    longboxed.api.publishers
    ~~~~~~~~~~~~~~~~~~~~

    Publisher endpoints
"""
from flask import Blueprint, jsonify, request

from ..models import Title, Publisher
from . import route


bp = Blueprint('publishers', __name__, url_prefix='/publishers')


@route(bp, '/', methods=['GET'])
def publishers():
    page = request.args.get('page', 1, type=int)
    pagination = Publisher.query.order_by(Publisher.name).\
                           paginate(page, per_page=50, error_out=False)
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
        'count': pagination.total
    })


@route(bp, '/<int:id>', methods=['GET'])
def get_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    return jsonify({
        'publisher': publisher.to_json()
    })


@route(bp, '/<int:id>/titles/', methods=['GET'])
def get_titles_for_publisher(id):
    publisher = Publisher.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = publisher.titles.order_by(Title.name).\
                              paginate(page, per_page=50, error_out=False)
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
        'count': pagination.total
    })