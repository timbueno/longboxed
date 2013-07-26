# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""
from flask.ext.login import UserMixin
# from mongoengine import EmbeddedDocument, EmbeddedDocumentField
# from mongoengine import (EmbeddedDocument, Document, StringField,
#                         FloatField, BooleanField, ListField,
#                         DateTimeField, EmbeddedDocumentField)
# from flask.ext.mongoengine

# from flask.ext.mongokit import Document

# from ..helpers import JsonSerializer


# def max_length(length):
#     def validate(value):
#         if len(value) <= length:
#             return True
#         raise Exception('%s must be at most %s characters long' % length)
#     return validate
from ..core import db


# class Comment(EmbeddedDocument):
#     content = StringField()

# class Page(Document):
#     comments = ListField(EmbeddedDocumentField(Comment))

class UserComics(db.EmbeddedDocument):
    favorites = db.SortedListField(db.StringField(), default=None)

class UserSettings(db.EmbeddedDocument):
    display_favs = db.BooleanField(default=False)
    default_cal = db.StringField(default=None)
    show_publishers = db.ListField(db.StringField(), default=None)

class UserTokens(db.EmbeddedDocument):
    refresh_token = db.StringField(default=None)
    access_token = db.StringField(default=None)
    expire_time = db.StringField(default=None)

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
    favorites = db.EmbeddedDocumentField(UserComics)
    settings = db.EmbeddedDocumentField(UserSettings)
    tokens = db.EmbeddedDocumentField(UserTokens)


    # favorites = db.SortedListField(db.StringField())
    # display_favs = db.BooleanField()
    # default_cal = db.StringField()
    # show_publishers = db.ListField(db.StringField())
    # refresh_token = db.StringField()
    # access_token = db.StringField()
    # expire_time = db.DateTimeField()

    def get_id(self):
        return self.userid




# class UserJsonSerializer(JsonSerializer):
#     __json_public__ = ['id', 'info.email']


# class User(Document, UserMixin):
#     structure = {
#         'id': unicode,
#         'info': {
#             'full_name': unicode,
#             'first_name': unicode,
#             'last_name': unicode,
#             'gender': unicode,
#             'birthday': datetime,
#             'email': unicode
#         },
#         'friends': [unicode],
#         'comics': {
#             'favorites': [unicode]
#         },
#         'settings': {
#             'display_favs': bool,
#             'default_cal': unicode,
#             'publishers': [unicode]
#         },
#         'tokens': {
#             'refresh_token': unicode,
#             'access_token': unicode,
#             'expire_time': datetime,

#         },
#         'date_creation': datetime,
#         'last_login': datetime,
#     }
#     validators = {
#         'info.full_name': max_length(50),
#         'info.email': max_length(120)
#     }
#     required_fields = ['id', 'info.email', 'date_creation']
#     default_values = {
#         'date_creation': datetime.utcnow,
#         'settings.display_favs': True
#     }
#     use_dot_notation = True
#     def __repr__(self):
#         return '<User %r>' % (self.name)

