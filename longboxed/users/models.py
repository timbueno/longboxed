# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""

from datetime import datetime

from flask.ext.login import UserMixin
from flask.ext.mongokit import Document

# from ..helpers import JsonSerializer


def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate


# class UserJsonSerializer(JsonSerializer):
#     __json_public__ = ['id', 'info.email']


class User(Document, UserMixin):
    structure = {
        'id': unicode,
        'info': {
            'full_name': unicode,
            'first_name': unicode,
            'last_name': unicode,
            'gender': unicode,
            'birthday': datetime,
            'email': unicode
        },
        'friends': [unicode],
        'comics': {
            'favorites': [unicode]
        },
        'settings': {
            'display_favs': bool,
            'default_cal': unicode,
            'publishers': [unicode]
        },
        'tokens': {
            'refresh_token': unicode,
            'access_token': unicode,
            'expire_time': datetime,

        },
        'date_creation': datetime,
        'last_login': datetime,
    }
    validators = {
        'info.full_name': max_length(50),
        'info.email': max_length(120)
    }
    required_fields = ['id', 'info.email', 'date_creation']
    default_values = {
        'date_creation': datetime.utcnow,
        'settings.display_favs': True
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.name)

