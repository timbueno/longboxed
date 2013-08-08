# -*- coding: utf-8 -*-
"""
    longboxed.users
    ~~~~~~~~~~~~~~

    longboxed users package
"""
from mongoengine.queryset import DoesNotExist
import requests

from ..core import Service
from .models import User

class UsersService(Service):
    __model__ = User

    def get_calendar_info(self, user):
        headers = {'Authorization': 'Bearer '+user.access_token}
        data = {'minAccessRole':'owner'}
        endpoint = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
        response = requests.get(endpoint, headers=headers, params=data)
        r = response.json()

        calendars = []
        default_cal = None
        for cal in r['items']:
            name = cal['summary']
            calid = cal['id']
            try:
                if cal['primary']:
                    default_cal = (cal['id'], cal['summary'], True)
                    primary = True
            except KeyError:
                primary = False

            calendars.append((calid, name, primary))

        return (default_cal, calendars)