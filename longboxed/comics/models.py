# -*- coding: utf-8 -*-
"""
    longboxed.comics.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    Comics module
"""
import re
from datetime import datetime

import requests

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_imageattach.entity import Image, image_attachment, store_context

from ..core import store, db, CRUDMixin


#: Many-to-Many relationship for bundles and issues helper table
issues_bundles = db.Table('issues_bundles',
    db.Column('bundle_id', db.Integer, db.ForeignKey('bundles.id')),
    db.Column('issue_id', db.Integer, db.ForeignKey('issues.id'))
)

issues_creators = db.Table('issues_creators',
    db.Column('creator_id', db.Integer, db.ForeignKey('creators.id')),
    db.Column('issue_id', db.Integer, db.ForeignKey('issues.id'))
)


class Publisher(db.Model, CRUDMixin):
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
    titles = db.relationship(
        'Title',
        backref=db.backref('publisher', lazy='joined'),
        lazy='dynamic'
    )
    comics = db.relationship(
        'Issue',
        backref=db.backref('publisher', lazy='joined'),
        lazy='dynamic'
    )

    def __str__(self):
        return self.name

    def to_json(self):
        p = {
            'id': self.id,
            'name': self.name,
            'title_count': self.titles.count(),
            'issue_count': self.comics.count()
        }
        return p

class Title(db.Model, CRUDMixin):
    """
    Title Model class with backreferenced relationship, issues. Publisher 
    can also be accessed with the hidden 'publisher' attribute.

    Example: Saga, East Of West

    Note: hybrid property is for sorting based on subscriber (user) number.
    # http://stackoverflow.com/questions/22876946/how-to-order-by-count-of-many-to-many-relationship-in-sqlalchemy
    """
    __tablename__ = 'titles'
    #: IDs
    id = db.Column(db.Integer(), primary_key=True)
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    #: Attributes
    name = db.Column(db.String(255))
    #: Relationships
    issues = db.relationship('Issue',
        backref=db.backref('title', lazy='joined'),
        lazy='dynamic',
        order_by='Issue.on_sale_date'
    )

    def __str__(self):
        return self.name

    @hybrid_property
    def num_subscribers(self):
        return self.users.count()

    @num_subscribers.expression
    def _num_subscribers_expression(cls):
        from ..users.models import titles_users
        return (db.select([db.func.count(titles_users.c.user_id).label('num_subscribers')])
                .where(titles_users.c.title_id == cls.id)
                .label('total_subscribers')
                )

    def to_json(self):
        t = {
            'id': self.id,
            'name': self.name,
            'publisher': {'id': self.publisher.id, 
                          'name': self.publisher.name},
            'issue_count': self.issues.count(),
            'subscribers': self.users.count()
        }
        return t

class Issue(db.Model, CRUDMixin):
    """
    Issue model class. Title and Publisher can both be referenced with
    the hidden 'publisher' and 'title' attributes

    Note: hybrid property is for sorting based on subscriber (user) number.
    # http://stackoverflow.com/questions/22876946/how-to-order-by-count-of-many-to-many-relationship-in-sqlalchemy
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
    prospective_release_date = db.Column(db.Date())
    genre = db.Column(db.String(100))
    people = db.Column(db.String(255)) #####
    popularity = db.Column(db.Float())
    last_updated = db.Column(db.DateTime())
    diamond_id = db.Column(db.String(100))
    discount_code = db.Column(db.String(1))
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

    def __str__(self):
        return self.complete_title

    def __cmp__(self, other_issue):
        id1 = int(re.search(r'\d+', self.diamond_id).group())
        id2 = int(re.search(r'\d+', other_issue.diamond_id).group())
        return id1 - id2

    @hybrid_property
    def num_subscribers(self):
        return self.title.users.count()

    @num_subscribers.expression
    def _num_subscribers_expression(cls):
        from ..users.models import titles_users
        return (db.select([db.func.count(titles_users.c.user_id).label('num_subscribers')])
                .where(titles_users.c.title_id == cls.title_id)
                .label('total_subscribers')
                )

    def to_json(self):
        i = {
            'id': self.id,
            'complete_title': self.complete_title,
            'publisher': {'id': self.publisher.id,
                          'name': self.publisher.name},
            'title': {'id': self.title.id,
                      'name': self.title.name},
            'price': self.retail_price,
            'diamond_id': self.diamond_id,
            'release_date': self.on_sale_date.strftime('%Y-%m-%d') if self.on_sale_date else None,
            'issue_number': self.issue_number,
            'cover_image': self.cover_image.find_thumbnail(width=500).locate(),
            'description': self.description
        }
        return i

    def set_cover_image_from_url(self, url, overwrite=False, default=False):
        """
        Downloads a jpeg file from a url and stores it in the image store.

        :param issue: :class:`Issue` object class
        :param url: URL to download the jpeg cover image format
        :param overwrite: Boolean flag that overwrites an existing image
        """
        created_flag = False
        if not self.cover_image.original or overwrite:
            print self.complete_title
            r = requests.get(url)
            if r.status_code == 200 and r.headers['content-type'] == 'image/jpeg':
                with store_context(store):
                    self.cover_image.from_blob(r.content)
                    self.save()
                    self.cover_image.generate_thumbnail(height=600)
                    self.save()
                    created_flag = True
        return created_flag

    def find_or_create_thumbnail(self, width=None, height=None):
        """
        Creates a thumbnail image from the original if one of the same size
        does not already exist. Width OR height must be provided. It is not
        necessary to provide both.

        Default Image (We should act on this in the future)
        http://affimg.tfaw.com/covers_tfaw/400/no/nocover.jpg

        :param issue: :class:`Issue` object class
        :param width: Width of desired thumbnail image
        :param height: Height of desired thumbnail image
        """
        assert width is not None or height is not None
        with store_context(store):
            try:
                image = self.cover_image.find_thumbnail(width=width, height=height)
            except NoResultFound:
                image = self.cover_image.generate_thumbnail(width=width, height=height)
            self.save()
        return image


class IssueCover(db.Model, Image):
    """
    Issue cover model
    """
    __tablename__ = 'issue_cover'

    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), primary_key=True)
    issue = db.relationship('Issue')


class Creator(db.Model, CRUDMixin):
    """
    Writers and/or Artists that create individual titles
    """
    __tablename__ = 'creators'

    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    #: Attributes
    name = db.Column(db.String(255))
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    # type = db.Column(db.String(255))
    creator_type = db.Column(db.Enum('writer', 'artist', 'other', name='creator_type'))
    issues = db.relationship(
        'Issue',
        secondary=issues_creators,
        backref=db.backref('creators', lazy='joined'),
        lazy='dynamic'
    )

    def __str__(self):
        return self.name

class Bundle(db.Model, CRUDMixin):
    """
    Bundle model class.

    Bundles are groupings of issues that contain a date and a link to a an
    owner. Owners are able to view previous weeks hauls.
    """
    __tablename__ = 'bundles'
    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #: Attributes
    last_updated = db.Column(db.DateTime())
    release_date = db.Column(db.Date())
    #: Relationships
    issues = db.relationship(
        'Issue',
        secondary=issues_bundles,
        backref=db.backref('bundles', lazy='dynamic')
    )

    def to_json(self):
        b = {
            'id': self.id,
            'release_date': self.release_date.strftime('%Y-%m-%d'),
            'last_updated': self.last_updated,
            'issues': [issue.to_json() for issue in self.issues]
        }
        return b