# -*- coding: utf-8 -*-
"""
    longboxed.comics.models
    ~~~~~~~~~~~~~

    Comics module
"""
from ..core import db

class Comic(db.Document):
    meta = {'collection': 'comics_test'}
    productID = db.StringField()
    name = db.StringField()
    issue_number = db.FloatField()
    issues = db.FloatField()
    other = db.StringField()
    complete_title = db.StringField()
    one_shot = db.BooleanField()
    alink = db.StringField()
    thumbnail = db.StringField()
    bigImage = db.StringField()
    retailPrice = db.FloatField()
    description = db.StringField()
    onSaleDate = db.DateTimeField()
    genre = db.StringField()
    people = db.ListField(db.StringField())
    popularity = db.FloatField()
    lastUpdated = db.DateTimeField()
    publisher = db.StringField()
    diamondid = db.StringField()
    category = db.StringField()
    upc = db.StringField()

# from flask.ext.mongokit import Document

# class Comic(Document):
#     structure = {
#         'productID': unicode, # 0
#         'info': { #1
#             'name': unicode,
#             'issue_number': float,
#             'issues': float,
#             'other': unicode,
#             'complete_title': unicode,
#             'one_shot': bool
#         },
#         'alink': unicode, # 4
#         'thumbnail': unicode, # 5
#         'bigImage': unicode, # 6
#         'retailPrice': float, # 8
#         'description': unicode, # 11
#         'onSaleDate': datetime, # 12
#         'genre': unicode, # 13
#         'people': unicode, # 14
#         'popularity': float, # 16
#         'lastUpdated': datetime, # 17
#         'publisher': unicode, # 19
#         'id': unicode, # 20
#         'category': unicode, # 21
#         'upc': unicode # 25
#     }
#     required_fields = ['id', 'info.complete_title']
#     use_dot_notation = True
#     def __repr__(self):
#         return '<Comic %r>' % (self.info.name)

#     def is_float(self, number):
#         try: 
#             float(number)
#             return True
#         except ValueError:
#             return False