# -*- coding: utf-8 -*-
"""
    longboxed.helpers
    ~~~~~~~~~~~~~~~~~

    longboxed helpers module
"""

import hashlib
import pkgutil
import importlib

from csv import DictReader
from datetime import datetime, timedelta
from HTMLParser import HTMLParser

from flask import Blueprint, request
from flask.json import JSONEncoder as BaseJSONEncoder
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


def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    return (path + args).encode('utf-8')


def compare_images(image1, image2):
    """Compares byte strings of two images by hashing them with md5
    if hashes are the same - return true
    if not return false.
    This is used primarily for checking if issues are missing a unique cover
    image from TFAW.
    """
    hash1 = hashlib.md5(image1).hexdigest()
    hash2 = hashlib.md5(image2).hexdigest()
    return hash1 == hash2


class JSONEncoder(BaseJSONEncoder):
    """Custom :class:`JSONEncoder` which respects objects that include the
    :class:`JsonSerializer` mixin.
    """
    def default(self, obj):
        if isinstance(obj, JsonSerializer):
            return obj.to_json()
        return super(JSONEncoder, self).default(obj)


def unicode_csv_reader(unicode_csv_data, fieldnames, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = DictReader(
            utf_8_encoder(unicode_csv_data),
            fieldnames=fieldnames,
            **kwargs
    )
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield dict([(key, unicode(value, 'utf-8')) for key, value in row.iteritems()])
        # yield [unicode(cell, 'utf-8') for cell in row]

def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


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


def week_handler(week):
    if type(week) == datetime.date:
        return week
    elif type(week) != str:
        raise Exception('week variable must be a date or a string type!')
    if week not in ['thisweek', 'nextweek', 'twoweeks']:
        raise Exception('Not a valid input for week selection')
    if week == 'thisweek':
        date = current_wednesday()
    if week == 'nextweek':
        date = next_wednesday()
    if week == 'twoweeks':
        date = two_wednesdays()
        # raise NotImplementedError
    return date


def get_week(date, multiplier=0):
    """
    Returns Sunday and Saturday of the week the 'date' argument is
    currently in.

    The 'multiplier' argument provides the ability to navigate multiple
    weeks into the future and past
    """
    day_idx = get_day_index(date)
    sunday = (date - timedelta(days=day_idx)) + (multiplier * timedelta(days=7))
    saturday = (sunday + timedelta(days=6))
    return (sunday, saturday)


def get_day_index(date):
    return (date.weekday() + 1) % 7 # Turn sunday into 0, monday into 1, etc.


def after_wednesday(date):
    day_index = get_day_index(date)
    if day_index > 3:
        return True
    else:
        return False


def next_n_weeks(date, n=1):
    """
    Returns the first sunday and last saturday of the range. This is useful to
    provide a lower and upper bound on SQL queries.
    """
    first_sunday, first_saturday = get_week(date)
    last_saturday = first_saturday + (n * timedelta(days=7))
    return (first_sunday, last_saturday)


def mail_content(recipients, sender, subject, content,
                 html=None, attachment=None):
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
        msg.attach(
                filename='checks.txt',
                content_type='text/plain',
                data=attachment
        )
    mail.send(msg)
    return


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"


def is_float(number):
    try:
        float(number)
        return True
    except (ValueError, TypeError):
        return False

def is_int(number):
    try:
        int(number)
        return True
    except(ValueError, TypeError):
        return False


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
