# -*- coding: utf-8 -*-
"""
    longboxed.users.models
    ~~~~~~~~~~~~~~~~~~~~~

    User models
"""
from datetime import datetime

from flask.ext.security import UserMixin, RoleMixin

from ..core import db, CRUDMixin

# Many-to-Many relationship for user defined publishers to display
publishers_users = db.Table('publishers_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('publisher_id', db.Integer, db.ForeignKey('publishers.id'))
)

# Many-to-Many relationship for user Pull Lists
titles_users = db.Table('titles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('title_id', db.Integer, db.ForeignKey('titles.id'))
)


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin, CRUDMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __eq__(self, other):
        return (self.name == other or
                self.name == getattr(other, 'name', None))

    def __ne__(self, other):
        return (self.name != other and
                self.name != getattr(other, 'name', None))

    def __str__(self):
        return self.name

    @classmethod
    def insert_roles(cls):
        roles = [('user', 'No Permissions'),
                 ('admin', 'Comic specific permissions'),
                 ('super', 'All permissions')]
        for r in roles:
            role = cls.query.filter_by(name=r[0]).first()
            if role is None:
                role = cls.create(name=r[0], description=r[1])
        return


class User(db.Model, UserMixin, CRUDMixin):
    __tablename__ = 'users'
    # ids
    id = db.Column(db.Integer, primary_key=True)
    # Attributes
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    full_name = db.Column(db.String(255))
    birthday = db.Column(db.Date())
    last_seen = db.Column(db.DateTime())

    # Flask-Security
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(80))
    current_login_ip = db.Column(db.String(80))
    login_count = db.Column(db.Integer, default=0)
    confirmed_at = db.Column(db.DateTime())

    #: Feature Settings
    display_pull_list = db.Column(db.Boolean, default=True)
    mail_bundles = db.Column(db.Boolean, default=True)

    # Relationships
    publishers = db.relationship(
        'Publisher',
        secondary=publishers_users,
        backref=db.backref('users', lazy='dynamic')
    )
    pull_list = db.relationship(
        'Title',
        secondary=titles_users,
        backref=db.backref('users', lazy='dynamic'),
        lazy='joined'
    )
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )
    bundles = db.relationship(
        'Bundle',
        backref=db.backref('user', lazy='joined'),
        lazy='dynamic'
    )

    def __str__(self):
        return self.email

    def to_json(self):
        u = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'roles': [role.name for role in self.roles]
        }
        return u

    def ping(self):
        self.last_seen = datetime.utcnow()
        self.save()
        return
