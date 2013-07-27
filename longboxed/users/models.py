# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""
from datetime import datetime

from flask.ext.login import UserMixin

from ..core import db


class UserComics(db.EmbeddedDocument):
    favorites = db.SortedListField(db.StringField(), default=None)


class UserSettings(db.EmbeddedDocument):
    display_favs = db.BooleanField(default=False)
    default_cal = db.StringField(default=None)
    show_publishers = db.ListField(db.StringField(), default=None)


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
    favorites = db.EmbeddedDocumentField(UserComics, default=UserComics)
    settings = db.EmbeddedDocumentField(UserSettings, default=UserSettings)
    tokens = db.EmbeddedDocumentField(UserTokens, default=UserTokens)

    def get_id(self):
        return self.userid