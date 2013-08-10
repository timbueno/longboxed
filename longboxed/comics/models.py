# -*- coding: utf-8 -*-
"""
    longboxed.comics.models
    ~~~~~~~~~~~~~

    Comics module
"""
from ..core import db


class Publisher(db.Model):
    __tablename__ = 'publishers'
    # __table_args__ = {'extend_existing': True}
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    name = db.Column(db.String(255))
    # Relationships
    titles = db.relationship('Title', backref='publisher', lazy='dynamic')


class Title(db.Model):
    __tablename__ = 'titles'
    # __table_args__ = {'extend_existing': True}
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    # Attributes
    name = db.Column(db.String(255))
    # Relationships
    issues = db.relationship('Issue', backref='title', lazy='dynamic')


class Issue(db.Model):
    __tablename__ = 'issues'
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.Integer, db.ForeignKey('titles.id'))
    # Attributes
    product_id = db.Column(db.String(100))
    issue_number = db.Column(db.Float)
    issues = db.Column(db.Float)
    other = db.Column(db.String(255))
    complete_title = db.Column(db.String(255))
    one_shot = db.Column(db.Boolean())
    a_link = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    big_image = db.Column(db.String(255))
    retail_price = db.Column(db.Float)
    description = db.Column(db.String(255))
    on_sale_date = db.Column(db.Date())
    genre = db.Column(db.String(100))
    people = db.Column(db.String(255)) #####
    popularity = db.Column(db.Float)
    last_updated = db.Column(db.DateTime())
    diamond_id = db.Column(db.String(100))
    category = db.Column(db.String(100))
    upc = db.Column(db.String(100))


# class Comic(db.Document):
#     meta = {'collection': 'comics_test'}
#     productID = db.StringField()
#     name = db.StringField()
#     issue_number = db.FloatField()
#     issues = db.FloatField()
#     other = db.StringField()
#     complete_title = db.StringField()
#     one_shot = db.BooleanField()
#     alink = db.StringField()
#     thumbnail = db.StringField()
#     bigImage = db.StringField()
#     retailPrice = db.FloatField()
#     description = db.StringField()
#     onSaleDate = db.DateTimeField()
#     genre = db.StringField()
#     people = db.ListField(db.StringField())
#     popularity = db.FloatField()
#     lastUpdated = db.DateTimeField()
#     publisher = db.StringField()
#     diamondid = db.StringField()
#     category = db.StringField()
#     upc = db.StringField()

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