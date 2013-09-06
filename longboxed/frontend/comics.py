# -*- coding: utf-8 -*-
"""
    longboxed.frontend.comics
    ~~~~~~~~~~~~~~~~~~

    Comics blueprints
"""
from datetime import datetime, timedelta

from flask import abort, current_app, Blueprint, jsonify, render_template, request
from flask.ext.security import current_user

from . import route
from ..services import comics as _comics


bp = Blueprint('comics', __name__)


@route(bp,'/comics')
def comics():
    start, end = get_current_week()
    dates = {}
    dates['today'] = end.strftime('%B %-d, %Y')
    dates['lastweek'] = start.strftime('%B %-d, %Y')
    dates['start'] = start
    dates['end'] = end
    comicList, matches = _comics.issues.find_relevent_issues_in_date_range(start, end, current_user)
    return render_template('comics.html', dates=dates, comicList=comicList, calendarenable=1, matches=matches)


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
        # issues = title.issues.limit(10).order_by()
        issues = title.issues.all()
        # issues = title.issues.limit(10)
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

    # comicList = find_comics_in_date_range(start, end)
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



def get_current_week():
    today = datetime.today()
    day_of_week = today.weekday()
    to_beginning_of_week = timedelta(days=day_of_week)
    beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
    to_end_of_week = timedelta(days= (6 - day_of_week))
    end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
    return (beginning_of_week, end_of_week)
