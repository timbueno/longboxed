# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""
# from datetime import datetime

# import requests
from flask.ext.login import UserMixin

from ..core import db


publishers_users = db.Table('publishers_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('publisher_id', db.Integer, db.ForeignKey('publishers.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    google_id = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    birthday = db.Column(db.Date())

    registered_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    login_count = db.Column(db.Integer)

    refresh_token = db.Column(db.String(100))
    access_token = db.Column(db.String(100))
    token_expire_at = db.Column(db.DateTime())

    display_pull_list = db.Column(db.Boolean, default=True)
    default_cal = db.Column(db.String(255))
    # publishers = db.relationship('Publisher', backref='users',
    #                              lazy='select')
    publishers = db.relationship('Publisher', secondary=publishers_users,
        backref=db.backref('users', lazy='dynamic'))
    pull_list = []

    def get_id(self):
        return self.google_id


# class UserSettings(db.EmbeddedDocument):
#     display_pull_list = db.BooleanField(default=False)
#     default_cal = db.StringField()
#     show_publishers = db.ListField(db.StringField(default=None))


# class UserTokens(db.EmbeddedDocument):
#     refresh_token = db.StringField(default=None)
#     access_token = db.StringField(default=None)
#     expire_time = db.DateTimeField(default=datetime.now())


# class User(db.Document, UserMixin):
#     # Save User document to this collection
#     meta = {'collection': 'users_test'}

#     userid = db.StringField()
#     full_name = db.StringField()
#     first_name = db.StringField()
#     last_name = db.StringField()
#     gender = db.StringField()
#     birthday = db.StringField()
#     email = db.EmailField()
#     friends = db.ListField(db.StringField())
#     date_creation = db.DateTimeField()
#     last_login = db.DateTimeField()
#     pull_list = db.SortedListField(db.StringField(default=None))
#     settings = db.EmbeddedDocumentField(UserSettings, default=UserSettings)
#     tokens = db.EmbeddedDocumentField(UserTokens, default=UserTokens)

#     def get_id(self):
#         return self.userid

#     def get_calendar_info(self):
#         headers = {'Authorization': 'Bearer '+self.tokens.access_token}
#         data = {'minAccessRole':'owner'}
#         endpoint = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
#         response = requests.get(endpoint, headers=headers, params=data)
#         r = response.json()

#         calendars = []
#         default_cal = None
#         for cal in r['items']:
#             name = cal['summary']
#             calid = cal['id']
#             try:
#                 if cal['primary']:
#                     default_cal = (cal['id'], cal['summary'], True)
#                     primary = True
#             except KeyError:
#                 primary = False

#             calendars.append((calid, name, primary))

#         return (default_cal, calendars)    