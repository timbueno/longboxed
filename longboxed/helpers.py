# -*- coding: utf-8 -*-
"""
    longboxed.helpers
    ~~~~~~~~~~~~~~~~

    longboxed helpers module
"""

import pkgutil
import importlib

from datetime import datetime, timedelta
from HTMLParser import HTMLParser

from flask import Blueprint
from json import JSONEncoder as BaseJSONEncoder


def register_blueprints(app, package_name, package_path):
    """Register all Blueprint instances on the specified Flask application found
    in all modules for the specified package.

    :param app: the Flask application
    :param package_name: the package name
    :param package_path: the package path
    """
    rv = []
    for _, name, _ in pkgutil.iter_modules(package_path):
        m = importlib.import_module('%s.%s' % (package_name, name))
        for item in dir(m):
            item = getattr(m, item)
            if isinstance(item, Blueprint):
                app.register_blueprint(item)
            rv.append(item)
    return rv


class JSONEncoder(BaseJSONEncoder):
    """Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        if isinstance(obj, JsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def wednesday(date):
    sunday, saturday = get_week(date)
    return sunday + timedelta(days=3)

def current_wednesday():
    return wednesday(datetime.today().date())

# This is going to cause problems when trying to import data on a sunday.
# def get_current_wednesday():
#     start, end = get_current_week()
#     return get_wednesday(start)

def get_week(date):
    """Returns Sunday through Saturday of the current week
    (Sunday first)"""
    day_idx = (date.weekday() + 1) % 7 # Turn sunday into 0, monday into 1, etc.
    sunday = date - timedelta(days=day_idx)
    saturday = sunday + timedelta(days=6)
    return (sunday, saturday)

# def get_current_week():
#     today = datetime.today()
#     day_of_week = today.weekday()
#     to_beginning_of_week = timedelta(days=day_of_week)
#     beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
#     # to_end_of_week = timedelta(days= (6 - day_of_week))
#     # end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
#     end_of_week = beginning_of_week + timedelta(days=6)
#     return (beginning_of_week.date(), end_of_week.date())

# def get_next_week():
#     start, end = get_current_week()
#     return (start+timedelta(days=7), end+timedelta(days=7))

class JsonSerializer(object):
    """A mixin that can be used to mark a SQLAlchemy model class which
    implements a :func:`to_json` method. The :func:`to_json` method is used
    in conjuction with the custom :class:`JSONEncoder` class. By default this
    mixin will assume all properties of the SQLAlchemy model are to be visible
    in the JSON output. Extend this class to customize which properties are
    public, hidden or modified before being being passed to the JSON serializer.
    """

    __json_public__ = None
    __json_hidden__ = None
    __json_modifiers__ = None

    def get_field_names(self):
        for p in self.__mapper__.iterate_properties:
            yield p.key

    def to_json(self):
        field_names = self.get_field_names()

        public = self.__json_public__ or field_names
        hidden = self.__json_hidden__ or []
        modifiers = self.__json_modifiers__ or dict()

        rv = dict()
        for key in public:
            rv[key] = getattr(self, key)
        for key, modifier in modifiers.items():
            value = getattr(self, key)
            rv[key] = modifier(value, self)
        for key in hidden:
            rv.pop(key, None)
        return rv