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

titles_users = db.Table('titles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('title_id', db.Integer, db.ForeignKey('titles.id'))
)


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    # ids
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
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
    # Relationships
    publishers = db.relationship('Publisher', secondary=publishers_users,
        backref=db.backref('users', lazy='dynamic'))
    pull_list = db.relationship('Title', secondary=titles_users,
        backref=db.backref('users', lazy='dynamic'), lazy='joined')

    def get_id(self):
        return self.google_id
