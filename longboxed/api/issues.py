# -*- coding: utf-8 -*-
"""
    longboxed.api.issues
    ~~~~~~~~~~~~~~~~~~~~

    Issue endpoints
"""

from flask import jsonify, Blueprint, request, make_response, json

from ..helpers import current_wednesday
from ..services import comics
from . import route


bp = Blueprint('issues', __name__, url_prefix='/issues')


@route(bp, '/thisweek/')
def this_week():
    date = current_wednesday()
    issues = comics.issues.find_issue_with_date(date, True)
    # response = make_response(json.dumps({'thing':'those'}))
    # return jsonify({
    #     # 'date': date.strftime('%Y-%m-%d'),
    #     # 'issues': issues[0].complete_title
    #     'thing': 'those'
    # })
    return {
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues if issue.is_parent]
    }