# -*- coding: utf-8 -*-
"""
    longboxed.helpers
    ~~~~~~~~~~~~~~~~~

    longboxed helpers module
"""

import pkgutil
import importlib

from datetime import datetime, timedelta
from HTMLParser import HTMLParser
from json import JSONEncoder as BaseJSONEncoder

from flask import Blueprint
from flask.ext.mail import Message

from .core import mail


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
    """Strips a string of all html tags"""
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def wednesday(date, multiplier=0):
    """Given a date, returns a Date() object containing the week's wednesday.
    A week is defined as Sunday thru Saturday. The 'multiplier' argument 
    provides the ability navigate multiple weeks into the future and past

    :param date: :class:`Date` object used to center in on desired week
    :param multiplier: :class:`int` object that moves the date forward or backward
    """
    sunday, saturday = get_week(date, multiplier)
    return sunday + timedelta(days=3)

def current_wednesday():
    """Gets the current weeks wednesday"""
    return wednesday(datetime.today().date())

def next_wednesday():
    """Gets next weeks wendesday"""
    return wednesday(datetime.today().date(), 1)

def two_wednesdays():
    """Gets two wednesdays from now"""
    return wednesday(datetime.today().date(), 2)

def last_wednesday():
    """Get last week's Wednesday as a :class:`Date` object"""
    return wednesday(datetime.today().date(), -1)


def get_week(date, multiplier=0):
    """Returns Sunday and Saturday of the week the 'date' argument is currently in.
    The 'multiplier' argument provides the ability to navigate multiple weeks into 
    the future and past"""
    day_idx = (date.weekday() + 1) % 7 # Turn sunday into 0, monday into 1, etc.
    sunday = (date - timedelta(days=day_idx)) + (multiplier * timedelta(7))
    saturday = (sunday + timedelta(days=6))
    return (sunday, saturday)


def mail_content(recipients, sender, subject, content, html=None, attachment=None):
    """
    Generic function allowing for easy sending of email. A :class:`Mail`
    from :module:`longboxed.core` must be in the applications context

    :param recipients: list of email address strings
    :param sender: sending email address
    :param subject: message subject string
    :param content: html content
    :param attachment: plain text attachment
    """
    msg = Message(subject,
                  sender=sender,
                  recipients=recipients,
                  body=content,
                  html=html
    )
    if attachment:
        msg.attach(filename='checks.txt', content_type='text/plain', data=attachment)
    mail.send(msg)
    return


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