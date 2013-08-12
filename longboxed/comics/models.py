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
    titles = db.relationship('Title', backref=db.backref('publisher', lazy='joined'), lazy='dynamic')
    comics = db.relationship('Issue', backref=db.backref('publisher', lazy='joined'), lazy='dynamic')


class Title(db.Model):
    __tablename__ = 'titles'
    # __table_args__ = {'extend_existing': True}
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    # Attributes
    name = db.Column(db.String(255))
    # Relationships
    issues = db.relationship('Issue', backref=db.backref('title', lazy='joined'), lazy='dynamic')


class Issue(db.Model):
    __tablename__ = 'issues'
    # IDs
    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.Integer, db.ForeignKey('titles.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
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
    description = db.Column(db.Text)
    on_sale_date = db.Column(db.DateTime())
    genre = db.Column(db.String(100))
    people = db.Column(db.String(255)) #####
    popularity = db.Column(db.Float)
    last_updated = db.Column(db.DateTime())
    diamond_id = db.Column(db.String(100))
    category = db.Column(db.String(100))
    upc = db.Column(db.String(100))