# -*- coding: utf-8 -*-
"""
    longboxed.frontend.calendar
    ~~~~~~~~~~~~~~~~~~

    Calendar blueprints
"""
from datetime import datetime, timedelta
import json
import sys

from dateutil import tz
from flask import Blueprint, jsonify, request
from flask.ext.security import current_user, login_required
import requests

from . import route
from ..services import comics as _comics


bp = Blueprint('calendar', __name__)


@route(bp, '/add_issue_to_cal')
@login_required
def add_issue_to_cal():
    try:
        diamond_id = request.args.get('id')
        issue = _comics.issues.first(diamond_id=diamond_id)
        if issue:
            event = {
                'summary': issue.complete_title,
                'description': issue.description,
                'start': {
                    'date': issue.on_sale_date.strftime('%Y-%m-%d')
                },
                'end': {
                    'date': issue.on_sale_date.strftime('%Y-%m-%d')
                }
            }
            response = insert_calendar_event(event)
            if response:
                return jsonify(response=200, title=str(issue.complete_title))
            else:
                return jsonify(response=201)
        return jsonify(response=500)
    except:
        print "Unexpected error [/add_issue_to_cal]:", sys.exc_info()[1]
        return jsonify(response=500)


def current_headers():
    headers = {'Authorization': 'Bearer '+current_user.access_token,
                'X-JavaScript-User-Agent':  'Google       APIs Explorer',
                'Content-Type':  'application/json'}
    return headers


def insert_calendar_event(new_event):
    headers = current_headers()
    endpoint = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % current_user.default_cal
    
    # Check all events on given day
    day = datetime.strptime(new_event['start']['date'], '%Y-%m-%d')
    events = events_on_day(current_user.default_cal, day)
    
    # Check if event has already been added based on summaries
    insert_event = True
    if events:
        for event in events:
            if event['summary'] == new_event['summary']:
                insert_event = False
                break
    if insert_event:
        response = requests.post(endpoint, headers=headers, data=json.dumps(new_event))
        return True
    return False


def events_on_day(cal, day):
    headers = current_headers()
    endpoint = endpoint = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % cal
    
    start = datetime(day.year, day.month, day.day, tzinfo=tz.tzutc())
    end = start + timedelta(1)
    data = {
        'timeMin': start.isoformat(),
        'timeMax': end.isoformat()
    }
    response = requests.get(endpoint, headers=headers, params=data)
    r = response.json()
    if 'items' in r:
        return r['items']
    # print 'NO EVENTS FOUND'
    return None