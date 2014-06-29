# -*- coding: utf-8 -*-
"""
    longboxed.api.issues
    ~~~~~~~~~~~~~~~~~~~~

    Issue endpoints
"""
from datetime import datetime

from flask import abort, Blueprint, request

from ..helpers import current_wednesday
from ..services import comics
from . import route


bp = Blueprint('issues', __name__, url_prefix='/issues')


@route(bp, '/')
def issues_with_date():
    date = request.args.get('date')
    if isinstance(date, datetime):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    issues = comics.issues.find_issue_with_date(date, True)
    return {
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues if issue.is_parent]
    }


@route(bp, '/<int:id>')
def get_issue(id):
    issue = comics.issues.get(id)
    return issue.to_json()


@route(bp, '/thisweek/')
def this_week():
    date = current_wednesday()
    issues = comics.issues.find_issue_with_date(date, True)
    return {
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues if issue.is_parent]
    }