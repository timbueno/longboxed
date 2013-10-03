# -*- coding: utf-8 -*-
"""
    longboxed.comics.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    Comics module
"""
from sqlalchemy_imageattach.entity import Image, image_attachment

from ..core import db


class Publisher(db.Model):
    """
    Publisher model class with two back referenced relationships, titles and issues.

    Example: Marvel Comics, Image Comics
    """
    __tablename__ = 'publishers'
    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    #: Attributes
    name = db.Column(db.String(255))
    #: Relationships
    titles = db.relationship('Title', backref=db.backref('publisher', lazy='joined'), lazy='dynamic')
    comics = db.relationship('Issue', backref=db.backref('publisher', lazy='joined'), lazy='dynamic')

    def __str__(self):
        return self.name

class Title(db.Model):
    """
    Title Model class with backreferenced relationship, issues. Publisher 
    can also be accessed with the hidden 'publisher' attribute.

    Example: Saga, East Of West
    """
    __tablename__ = 'titles'
    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    #: Attributes
    name = db.Column(db.String(255))
    #: Relationships
    issues = db.relationship('Issue', backref=db.backref('title', lazy='joined'), lazy='dynamic', order_by='Issue.on_sale_date')

    def __str__(self):
        return self.name

class Issue(db.Model):
    """
    Issue model class. Title and Publisher can both be referenced with
    the hidden 'publisher' and 'title' attributes
    """
    __tablename__ = 'issues'
    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    title_id = db.Column(db.Integer, db.ForeignKey('titles.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    #: Attributes
    product_id = db.Column(db.String(100))
    issue_number = db.Column(db.Numeric(precision=6, scale=2))
    issues = db.Column(db.Numeric(precision=6, scale=2))
    other = db.Column(db.String(255))
    complete_title = db.Column(db.String(255))
    one_shot = db.Column(db.Boolean(), default=False)
    a_link = db.Column(db.String(255))
    thumbnail = db.Column(db.String(255))
    big_image = db.Column(db.String(255))
    retail_price = db.Column(db.Float())
    description = db.Column(db.Text())
    on_sale_date = db.Column(db.Date())
    current_tfaw_release_date = db.Column(db.Date())
    genre = db.Column(db.String(100))
    people = db.Column(db.String(255)) #####
    popularity = db.Column(db.Float())
    last_updated = db.Column(db.DateTime())
    diamond_id = db.Column(db.String(100))
    category = db.Column(db.String(100))
    upc = db.Column(db.String(100))
    #: Relationships
    cover_image = image_attachment('IssueCover')
    is_parent = db.Column(db.Boolean(), default=False)
    has_alternates = db.Column(db.Boolean(), default=False)
    @property
    def alternates(self):
        return self.query.filter(Issue.title==self.title, Issue.issue_number==self.issue_number, \
                                 Issue.diamond_id!=self.diamond_id)


class IssueCover(db.Model, Image):
    """
    Issue cover model
    """
    __tabelname__ = 'issue_cover'

    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), primary_key=True)
    issue = db.relationship('Issue')


