# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""

from flask import abort, Blueprint, render_template, g
from flask.ext.login import (current_user, login_required,
                            login_user, logout_user, confirm_login,
                            fresh_login_required)

from . import route
from ..services import comics as _comics

from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)


@route(bp, '/')
def index():
    if not current_user.is_anonymous():
        return render_template('main.html')
    return render_template('main.html')

@route(bp, '/favorites')
def favorites():
    return abort(404)

# @route(bp, '/favorites')
# def favorites():
#     return abort(404)

@route(bp, '/settings')
def settings():
    return abort(404)

@route(bp,'/comics')
def comics():
    start, end = get_current_week()
    dates = {}
    dates['today'] = end.strftime('%B %-d, %Y')
    dates['lastweek'] = start.strftime('%B %-d, %Y')
    dates['start'] = start
    dates['end'] = end
    comicList = _comics.find_comics_in_date_range(start, end)
    print comicList[0].diamondid
    return render_template('comics.html', dates=dates, comicList=comicList, calendarenable=1, matches=None)


@route(bp, '/issue/<diamondid>')
def issue(diamondid):
    """Individual issue page"""
    # try:
    # print 'DIAMONDID ', diamondid
    issue = _comics.find_comic_with_diamondid(diamondid)
    # print 'ISSUE ', issue
    if issue:
        return render_template('issue.html', issue=issue)
    return abort(404) 

def get_current_week():
    today = datetime.today()
    day_of_week = today.weekday()
    to_beginning_of_week = timedelta(days=day_of_week)
    beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
    to_end_of_week = timedelta(days= (6 - day_of_week))
    end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
    return (beginning_of_week, end_of_week)