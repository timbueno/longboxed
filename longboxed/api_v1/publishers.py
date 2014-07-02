# -*- coding: utf-8 -*-
"""
    longboxed.api.publishers
    ~~~~~~~~~~~~~~~~~~~~

    Publisher endpoints
"""
from flask import Blueprint, jsonify

from ..services import comics
from . import route


bp = Blueprint('publishers', __name__, url_prefix='/publishers')


@route(bp, '/', methods=['GET'])
def publishers():
    publishers = comics.publishers.all()
    return jsonify({
        'publishers': [publisher.to_json() for publisher in publishers]
    })


@route(bp, '/<int:id>', methods=['GET'])
def get_publisher(id):
    publisher = comics.publishers.get(id)
    return jsonify(publisher.to_json())


@route(bp, '/<int:id>/titles/', methods=['GET'])
def get_titles_for_publisher(id):
    publisher = comics.publishers.get(id)
    return jsonify({
        'publisher': publisher.name,
        'titles': [title.to_json() for title in publisher.titles]
    })