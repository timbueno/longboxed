# -*- coding: utf-8 -*-
"""
    longboxed.frontend.comics
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Comics blueprints
"""
from datetime import datetime

from flask import abort, Blueprint, render_template, redirect, url_for

from . import route
from ..helpers import current_wednesday, last_wednesday, next_wednesday
from ..services import comics as _comics
from ..models import Issue, Title, Publisher


bp = Blueprint('comics', __name__)

# @route(bp,'/comics')
# def comics():
#     date = datetime.strptime('2013-11-20', '%Y-%m-%d')
#     # issues = _comics.issues.find_issue_with_date(date, True)
#     return render_template('releases_test.html', issues=issues, date=date)


@route(bp,'/releases/<date>')
def releases(date):
    try:
        if isinstance(date, datetime):
            pass
        elif isinstance(date, unicode):
            date = datetime.strptime(date, '%Y-%m-%d')
        else:
            return abort(404)
        # issues = _comics.issues.find_issue_with_date(date, True)
        issues = Issue.query.filter(Issue.on_sale_date==date, Issue.is_parent==True)
        return render_template('releases.html', date=date, issues=issues)
    except ValueError:
        return abort(404)


@route(bp, '/thisweek')
def this_week():
    date = current_wednesday()
    date = date.strftime('%Y-%m-%d')
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/lastweek')
def last_week():
    date = last_wednesday()
    date = date.strftime('%Y-%m-%d')
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/nextweek')
def next_week():
    date = next_wednesday()
    date = date.strftime('%Y-%m-%d')
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/issue/<diamond_id>')
def issue(diamond_id):
    """Individual issue page"""
    # issue = _comics.issues.first_or_404(diamond_id=diamond_id)
    issue = Issue.query.filter_by(diamond_id=diamond_id).first_or_404()
    if issue:
        return render_template('issue.html', issue=issue)
    return abort(404)


@route(bp, '/title/<title_id>')
def title(title_id):
    """Title page"""
    """TODO change comic_title to title. Problem with base template"""
    """TODO title model to get issues to 'select' change back to dynamic"""
    # title = _comics.titles.get_or_404(id=title_id)
    title = Title.query.get_or_404(title_id)
    if title:
        issues = title.issues.all()
        return render_template('title.html', comic_title=title, issues=issues)
    return abort(404)


@route(bp, '/publisher/<pub_id>')
def publisher(pub_id):
    """Publisher Page"""
    # publisher = _comics.publishers.get_or_404(id=pub_id)
    publisher = Publisher.query.get_or_404(pub_id)
    titles = publisher.titles.all()
    return render_template('publisher.html', publisher=publisher, titles=titles)
