# -*- coding: utf-8 -*-
"""
    longboxed.api.issues
    ~~~~~~~~~~~~~~~~~~~~

    Issue endpoints
"""
from datetime import datetime

from flask import abort, Blueprint, jsonify, request

from ..helpers import current_wednesday
from ..models import Issue
from . import route


bp = Blueprint('issues', __name__, url_prefix='/issues')


@route(bp, '/', methods=['GET'])
def issues_with_date():
    if 'date' not in request.args.keys():
        abort(404)
    date = request.args.get('date')
    if isinstance(date, datetime):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    issues = Issue.query.filter(Issue.on_sale_date==date, Issue.is_parent==True).all()
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues if issue.is_parent]
    })


@route(bp, '/<int:id>', methods=['GET'])
def get_issue(id):
    issue = Issue.query.get_or_404(id)
    return jsonify({
        'issue': issue.to_json()
    })


@route(bp, '/thisweek/', methods=['GET'])
def this_week():
    date = current_wednesday()
    issues = Issue.query.filter(Issue.on_sale_date==date, Issue.is_parent==True).all()
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues]
    })