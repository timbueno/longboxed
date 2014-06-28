# -*- coding: utf-8 -*-
"""
    longboxed.api.titles
    ~~~~~~~~~~~~~~~~~~~~

    Title endpoints
"""

from flask import Blueprint

from ..services import comics
from . import route


bp = Blueprint('titles', __name__, url_prefix='/titles')


@route(bp, '/')
def titles():
    titles = comics.titles.all()
    return {
        'titles': [title.to_json() for title in titles]
    }


@route(bp, '/<int:id>')
def get_title(id):
    title = comics.titles.get(id)
    return title.to_json()


@route(bp, '/<int:id>/issues/')
def get_issues_for_title(id):
    title = comics.titles.get(id)
    return {
        'title': title.name,
        'issues': [issue.to_json(description=False) for issue in title.issues]
    }