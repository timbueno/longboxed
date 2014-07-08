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
    page = request.args.get('page', 1, type=int)
    date = request.args.get('date')
    if isinstance(date, datetime):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    pagination = Issue.query.filter(Issue.on_sale_date==date, Issue.is_parent==True).\
                         paginate(page, per_page=50, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'issues': [issue.to_json() for issue in issues]
    })


@route(bp, '/<int:id>', methods=['GET'])
def get_issue(id):
    issue = Issue.query.get_or_404(id)
    return jsonify({
        'issue': issue.to_json()
    })


@route(bp, '/thisweek/', methods=['GET'])
def this_week():
    page = request.args.get('page', 1, type=int)
    date = current_wednesday()
    pagination = Issue.query.filter(Issue.on_sale_date==date, Issue.is_parent==True).\
                         paginate(page, per_page=50, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'prev': prev,
        'next': next,
        'count': pagination.total,
        'issues': [issue.to_json() for issue in issues]
    })