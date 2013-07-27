# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""
from datetime import datetime

from flask.ext.login import UserMixin

from ..core import db


class UserSettings(db.EmbeddedDocument):
    display_pull_list = db.BooleanField(default=False)
    default_cal = db.StringField()
    show_publishers = db.ListField(db.StringField(default=None))


class UserTokens(db.EmbeddedDocument):
    refresh_token = db.StringField(default=None)
    access_token = db.StringField(default=None)
    expire_time = db.DateTimeField(default=datetime.now())


class User(db.Document, UserMixin):
    # Save User document to this collection
    meta = {'collection': 'users_test'}

    userid = db.StringField()
    full_name = db.StringField()
    first_name = db.StringField()
    last_name = db.StringField()
    gender = db.StringField()
    birthday = db.StringField()
    email = db.EmailField()
    friends = db.ListField(db.StringField())
    date_creation = db.DateTimeField()
    last_login = db.DateTimeField()
    pull_list = db.SortedListField(db.StringField(default=None))
    settings = db.EmbeddedDocumentField(UserSettings, default=UserSettings)
    tokens = db.EmbeddedDocumentField(UserTokens, default=UserTokens)

    def get_id(self):
        return self.userid