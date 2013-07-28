# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""
import sys
from datetime import datetime, timedelta

from flask import abort, Blueprint, redirect, render_template, request, url_for
from flask.ext.login import (current_user, login_required)
from flask.ext.wtf import Form, BooleanField, SelectField, SelectMultipleField

from . import route
from ..services import comics as _comics


bp = Blueprint('dashboard', __name__)


@route(bp, '/')
def index():
    if not current_user.is_anonymous():
        start, end = 1, 2
        return render_template('main.html')
    return render_template('main.html')


@route(bp, '/favorites')
def favorites():
    print _comics.distinct_publishers()
    return abort(404)


@route(bp, '/settings', methods=['GET','POST'])
@login_required
def settings():
    if current_user is not None:
        if request.method == 'POST':
            try:
                if 'display_favs' in request.values:
                    current_user.settings.display_pull_list = True
                else:
                    current_user.settings.display_pull_list = False
                current_user.settings.default_cal = request.form['cals']
                current_user.settings.show_publishers = request.form.getlist('publishers')
                current_user.save()
            except:
                print "Unexpected error:", sys.exc_info()[0]
    else:
        return redirect(url_for('index'))

    # Default calendars
    calendars = current_user.get_calendar_info() # Get a users calendar
    c = []
    for cal in calendars[1]:
        c.append((cal[0], cal[1]))
    # Set the default calendar
    default_cal = current_user.settings.default_cal

    # Get all publishers
    pubs = [(p, p) for p in _comics.distinct_publishers() if p != '']
    pubs.sort()
    # Get user defaults
    user_pubs = current_user.settings.show_publishers

    class ExampleForm(Form):
        display_favs = BooleanField(
                            'Display Favorites',
                            description=u'If a comic on your favorites list matches an issue out that week, display it inline with the other books.', 
                            default = current_user.settings.display_pull_list)
        cals = SelectField(
                    u'Calendars',
                    description=u'Set the calendar the you want to add comics to.',
                    choices=c,
                    default=default_cal)
        publishers = SelectMultipleField(
            u'Publishers',
            {'title':'Select Publishers'},
            description=u'Publishers to display (selecting none displays all)',
            choices=pubs,
            default=user_pubs
        )

    form = ExampleForm()

    return render_template('settings.html',form=form)


# @route(bp,'/comics')
# def comics():
#     start, end = get_current_week()
#     dates = {}
#     dates['today'] = end.strftime('%B %-d, %Y')
#     dates['lastweek'] = start.strftime('%B %-d, %Y')
#     dates['start'] = start
#     dates['end'] = end
#     comicList = _comics.find_comics_in_date_range(start, end)
#     print comicList[0].diamondid
#     return render_template('comics.html', dates=dates, comicList=comicList, calendarenable=1, matches=None)


# @route(bp, '/issue/<diamondid>')
# def issue(diamondid):
#     """Individual issue page"""
#     issue = _comics.find_comic_with_diamondid(diamondid)
#     if issue:
#         return render_template('issue.html', issue=issue)
#     return abort(404) 


# def get_current_week():
#     today = datetime.today()
#     day_of_week = today.weekday()
#     to_beginning_of_week = timedelta(days=day_of_week)
#     beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
#     to_end_of_week = timedelta(days= (6 - day_of_week))
#     end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
#     return (beginning_of_week, end_of_week)