# -*- coding: utf-8 -*-
"""
    longboxed.api.issues
    ~~~~~~~~~~~~~~~~~~~~

    Issue endpoints
"""
from datetime import datetime
from datetime import date as _date

from flask import abort, Blueprint, jsonify, request

from ..core import cache
from ..helpers import current_wednesday, next_wednesday, make_cache_key
from ..models import Issue
from . import route


bp = Blueprint('issues', __name__, url_prefix='/issues')


@route(bp, '/', methods=['GET'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def issues_with_date():
    if 'date' not in request.args.keys():
        abort(404)
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    date = request.args.get('date')
    if isinstance(date, _date):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    pagination = Issue.query.filter(
                                Issue.on_sale_date==date,
                                Issue.is_parent==True)\
                            .paginate(page, per_page=count, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/<int:id>', methods=['GET'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def get_issue(id):
    issue = Issue.query.get_or_404(id)
    return jsonify({
        'issue': issue.to_json()
    })


@route(bp, '/thisweek/', methods=['GET'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def this_week():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    date = current_wednesday()
    pagination = Issue.query.filter(
                                Issue.on_sale_date==date,
                                Issue.is_parent==True)\
                             .paginate(page, per_page=50, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/nextweek/', methods=['GET'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def next_week():
    page = request.args.get('page', 1, type=int)
    count = request.args.get('count', 50, type=int)
    date = next_wednesday()
    pagination = Issue.query.filter(
                                Issue.on_sale_date==date,
                                Issue.is_parent==True)\
                            .paginate(page, per_page=50, error_out=False)
    issues = pagination.items
    prev = None
    if pagination.has_prev:
        prev = page-1
    next = None
    if pagination.has_next:
        next = page+1
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues],
        'prev': prev,
        'next': next,
        'total': pagination.total,
        'count': count
    })


@route(bp, '/popular/', methods=['GET'])
@cache.cached(timeout=300, key_prefix=make_cache_key)
def popular_issues_with_date():
    date = request.args.get('date', current_wednesday())
    print date
    if isinstance(date, _date):
        pass
    elif isinstance(date, unicode):
        date = datetime.strptime(date, '%Y-%m-%d')
    else:
        return abort(404)
    issues = Issue.query.filter(
                            Issue.on_sale_date==date,
                            Issue.is_parent==True)\
                         .order_by(Issue.num_subscribers.desc())\
                         .limit(10)\
                         .all()
    return jsonify({
        'date': date.strftime('%Y-%m-%d'),
        'issues': [issue.to_json() for issue in issues]
    })
