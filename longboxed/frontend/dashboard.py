# -*- coding: utf-8 -*-
"""
    longboxed.frontend.dashboard
    ~~~~~~~~~~~~~~~~~~

    Frontend blueprints
"""
# import sys
# from datetime import datetime, timedelta

from flask import Blueprint, g,redirect, render_template, request, url_for
from flask.ext.security import (current_user, login_required)
from flask.ext.wtf import Form
from wtforms import BooleanField, SelectField, SelectMultipleField

from . import route
from ..services import comics as _comics
from ..services import users as _users


bp = Blueprint('dashboard', __name__)

@bp.before_app_request
def before_request():
    if not current_user.is_anonymous():
        g.user = current_user
    else:
        g.user = None


@route(bp, '/')
def index():
    if not current_user.is_anonymous():
        start, end = 1, 2
        return render_template('main.html')
    return render_template('main.html')


@route(bp, '/settings', methods=['GET','POST'])
@login_required
def settings():
    if current_user is not None:
        if request.method == 'POST':
            if 'display_favs' in request.values:
                current_user.display_pull_list = True
            else:
                current_user.display_pull_list = False
            current_user.default_cal = request.form['cals']

            pubs = [long(e) for e in request.form.getlist('publishers')]
            p = _comics.publishers.get_all(*pubs)
            current_user.publishers = p
            _users.save(current_user)
    else:
        return redirect(url_for('index'))

    # Default calendars
    calendars = _users.get_calendar_info(current_user) # Get a users calendar
    c = []
    for cal in calendars[1]:
        c.append((cal[0], cal[1]))
    # Set the default calendar
    default_cal = current_user.default_cal

    # Get all publishers
    pubs = [(p.id, p.name) for p in _comics.publishers.all() if p.name != ''] #########
    pubs.sort()
    # Get user defaults
    user_pubs = [p.id for p in current_user.publishers if p.name !='']



    class ExampleForm(Form):
        display_favs = BooleanField(
                            'Display Favorites',
                            description=u'If a comic on your favorites list matches an issue out that week, display it inline with the other books.', 
                            default = current_user.display_pull_list)
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