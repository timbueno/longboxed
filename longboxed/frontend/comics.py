# -*- coding: utf-8 -*-
"""
    longboxed.frontend.comics
    ~~~~~~~~~~~~~~~~~~

    Comics blueprints
"""
from datetime import datetime

from flask import abort, Blueprint, jsonify, render_template, redirect, request, \
                  url_for
from flask.ext.security import current_user

from . import route
from ..helpers import current_wednesday, get_week, wednesday
from ..services import comics as _comics


bp = Blueprint('comics', __name__)

@route(bp,'/comics')
def comics():
    start, end = get_week(datetime.today().date())
    dates = {}
    dates['today'] = end.strftime('%B %-d, %Y')
    dates['lastweek'] = start.strftime('%B %-d, %Y')
    dates['start'] = start
    dates['end'] = end
    comicList, matches = _comics.issues.find_relevent_issues_in_date_range(start, end, current_user)
    return render_template('comics.html', dates=dates, comicList=comicList, calendarenable=1, matches=matches)


@route(bp,'/releases/<date>')
def releases(date):
    try:
        release_date = datetime.strptime(date, '%Y-%m-%d')
        issues = _comics.issues.find_issue_with_date(release_date)
        return render_template('releases.html', date=release_date, comicList=issues, calendarenable=1, matches=None)
    except ValueError:
        return abort(404)


@route(bp, '/thisweek')
def this_week():
    date = current_wednesday()
    date = date.strftime('%Y-%m-%d')
    print date
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/lastweek')
def last_week():
    date = wednesday(datetime.today().date(), -1)
    date = date.strftime('%Y-%m-%d')
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/nextweek')
def next_week():
    date = wednesday(datetime.today().date(), 1)
    date = date.strftime('%Y-%m-%d')
    return redirect(url_for('comics.releases', date=date))


@route(bp, '/issue/<diamond_id>')
def issue(diamond_id):
    """Individual issue page"""
    issue = _comics.issues.first_or_404(diamond_id=diamond_id)
    if issue:
        return render_template('issue.html', issue=issue)
    return abort(404)


@route(bp, '/title/<title_id>')
def title(title_id):
    """Title page"""
    """TODO change comic_title to title. Problem with base template"""
    """TODO title model to get issues to 'select' change back to dynamic"""
    title = _comics.titles.get_or_404(id=title_id)
    if title:
        issues = title.issues.all()
        return render_template('title.html', comic_title=title, issues=issues)
    return abort(404)


@route(bp, '/publisher/<pub_id>')
def publisher(pub_id):
    """Publisher Page"""
    publisher = _comics.publishers.get_or_404(id=pub_id)
    titles = publisher.titles.all()
    return render_template('publisher.html', publisher=publisher, titles=titles)



@route(bp, '/ajax/get_comicpage', methods=['POST'])
def get_comicpage():
    start = datetime.strptime(request.form['start'], '%B %d, %Y')
    end = datetime.strptime(request.form['end'], '%B %d, %Y')

    comicList, matches = _comics.find_relevent_comics_in_date_range(start, end, current_user)

    try:
        nav = render_template('comicsidenav.html', comicList=comicList)
    except:
        nav = None
    try:
        clist = render_template('comiclist.html', comicList=comicList)
    except:
        clist = None
    try:
        if matches:
            matches = render_template('favorite_matches.html', matches=matches)
    except:
        matches = None

    # return the html as json for jquery to insert
    return jsonify(nav=nav, clist=clist, matches=matches)
