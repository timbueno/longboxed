# -*- coding: utf-8 -*-
"""
    longboxed.comics.models
    ~~~~~~~~~~~~~~~~~~~~~~~

    Comics module
"""
import re
from copy import deepcopy
from datetime import datetime, timedelta
from decimal import Decimal
from HTMLParser import HTMLParser

import requests
from requests.exceptions import Timeout

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_imageattach.entity import Image, image_attachment, store_context

from ..core import store, db, CRUDMixin
from ..helpers import is_float


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
    Publisher model class with two back referenced relationships, titles and
    issues.

    Example: Marvel Comics, Image Comics
    """
    __tablename__ = 'publishers'
    #: IDs
    id = db.Column(db.Integer, primary_key=True)
    #: Attributes
    name = db.Column(db.String(255))
    #: Images
    logo = image_attachment('PublisherLogo')
    logo_bw = image_attachment('PublisherLogoBW')
    splash = image_attachment('PublisherSplash')
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

    @classmethod
    def from_raw(cls, record):
        record = deepcopy(record)
        created = 0
        try:
            name = record.get('publisher')
            publisher = cls.query.filter_by(name=name).first()
            if not publisher:
                publisher = cls.create(name=name)
                created = created + 1
        except Exception, err:
            print 'Publisher failed creation: ', record.get('publisher')
            print 'Error: ', err
            db.session.rollback()
            publisher = None
        return (publisher, created)

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

    def set_logo(self, image, overwrite=False):
        if not self.logo.original or overwrite:
            try:
                print 'Setting logo image for %s...' % self.name
                with store_context(store):
                    image = self.logo.from_file(image)
                    self.save()
            except Exception:
                print 'Could not set %s logo, rolling back session' % self.name
                db.session.rollback()

    def set_logo_bw(self, image, overwrite=False):
        if not self.logo_bw.original or overwrite:
            try:
                print 'Setting b&w logo image for %s...' % self.name
                with store_context(store):
                    image = self.logo_bw.from_file(image)
                    self.save()
            except Exception:
                print 'Could not set %s logo, rolling back session' % self.name
                db.session.rollback()

    def set_splash(self, image, overwrite=False):
        if not self.splash.original or overwrite:
            try:
                print 'Setting b&w logo image for %s...' % self.name
                with store_context(store):
                    image = self.splash.from_file(image)
                    self.save()
            except Exception:
                print 'Could not set %s splash rolling back session' % self.name
                db.session.rollback()

    @classmethod
    def set_images(cls, overwrite=False):
        for pub in cls.query.all():
            name = pub.name.lower()
            name = name.replace(' ', '_')
            try:
                if not pub.logo.original or overwrite:
                    file_path = 'media/publisher_images/%s.png' % name
                    with open(file_path, 'rb') as f:
                        pub.set_logo(f, overwrite)
            except IOError:
                print 'No logo found for %s' % pub.name
                print '    File path: %s' % file_path
            try:
                if not pub.logo_bw.original or overwrite:
                    file_path = 'media/publisher_images/%s_bw.png' % name
                    with open(file_path, 'rb') as f:
                        pub.set_logo_bw(f, overwrite)
            except IOError:
                print 'No black and white logo  found for %s' % pub.name
                print '    File path: %s' % file_path
            try:
                if not pub.splash.original or overwrite:
                    file_path = 'media/publisher_images/%s_splash.png' % name
                    with open(file_path, 'rb') as f:
                        pub.set_splash(f, overwrite)
            except IOError:
                print 'No splash image found for %s' % pub.name
                print '    File path: %s' % file_path


class PublisherLogo(db.Model, Image):
    """
    Color publisher logo
    """
    __tablename__ = 'publisher_logo'

    publisher_id = db.Column(
            db.Integer,
            db.ForeignKey('publishers.id'),
            primary_key=True)
    publisher = db.relationship('Publisher')


class PublisherLogoBW(db.Model, Image):
    """
    Black and white publisher logo
    """
    __tablename__ = 'publisher_logo_bw'

    publisher_id = db.Column(
            db.Integer,
            db.ForeignKey('publishers.id'),
            primary_key=True)
    publisher = db.relationship('Publisher')


class PublisherSplash(db.Model, Image):
    """
    Slash image for publisher object
    """
    __tablename__ = 'publisher_splash'

    publisher_id = db.Column(
            db.Integer,
            db.ForeignKey('publishers.id'),
            primary_key=True)
    publisher = db.relationship('Publisher')


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

    @classmethod
    def from_raw(cls, record):
        record = deepcopy(record)
        # Complete Title
        complete_title = ''
        try:
            complete_title = record.get('complete_title')
            m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', complete_title).groupdict()
        except (AttributeError, TypeError):
            m = None
        finally:
            pass

        created = 0
        try:
            name = m.get('title')
            title = cls.query.filter_by(name=name).first()
            if not title:
                title = cls.create(name=name)
                created = created + 1
        except Exception, err:
            print 'Title failed creation: ', complete_title
            print 'Error: ', err
            db.session.rollback()
            title = None
        return (title, created)

    def __str__(self):
        return self.name

    @hybrid_property
    def num_subscribers(self):
        return self.users.count()

    @num_subscribers.expression
    def _num_subscribers_expression(cls):
        from ..users.models import titles_users
        return (db.select(
                    [db.func.count(titles_users.c.user_id)\
                            .label('num_subscribers')])\
                   .where(titles_users.c.title_id == cls.id)\
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
        return self.query.filter(
                Issue.title==self.title,
                Issue.issue_number==self.issue_number,
                Issue.diamond_id!=self.diamond_id).all()

    @classmethod
    def from_raw(cls, record, sas_id='YOURUSERID'):
        # Create Issue dictionary
        i = deepcopy(record)

        # Complete Title
        try:
            complete_title = record.get('complete_title')
            # m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>(\d+))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', title).groupdict()
            m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', complete_title).groupdict()
            i['complete_title'] = complete_title
            if m['issue_number']:
                i['issue_number'] = Decimal(m['issue_number'])
            if m['issues']:
                i['issues'] = Decimal(m['issues'])
            if m.get('other'):
                i['other'] = m['other'].strip('()')
        except (AttributeError, TypeError):
            i['complete_title'] = ''
            m = None

        # Retail Price
        try:
            retail_price = record.get('retail_price')
            i['retail_price'] = float(retail_price) if is_float(retail_price) else None
        except Exception, err:
            i['retail_price'] = 0.00

        # Affiliate Link
        try:
            a_link = record.get('a_link')
            i['a_link'] = a_link.replace('YOURUSERID', sas_id)
        except Exception, err:
            i['a_link'] = None

        # Diamond ID
        try:
            diamond_id = record.get('diamond_id')
            if diamond_id[-1:].isalpha():
                i['diamond_id'] = diamond_id[:-1]
                i['discount_code'] = diamond_id[-1:]
            else:
                i['diamond_id'] = diamond_id
                i['discount_code'] = None
        except Exception, err:
            i['diamond_id'] = None
            i['discount_code'] = None

        # Description
        try:
            description = record.get('description')
            i['description'] = HTMLParser().unescape(description)
        except Exception, err:
            i['description'] = None

        # Prospective Release Date
        try:
            prospective_release_date = record.get('prospective_release_date')
            i['prospective_release_date'] = datetime.strptime(prospective_release_date, '%Y-%m-%d').date()
        except Exception, err:
            pass
            # i['prospective_release_date'] = None

        # Last Updated
        try:
            last_updated = record.get('last_updated')
            i['last_updated'] = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
        except Exception, err:
            pass

        # Clean Dictionary
        i.pop('publisher', None)
        i.pop('title', None)
        i.pop('people', None)
        i.pop('creators', None)

        # Create Issue Object
        created = 0
        try:
            # Create Issue object
            issue = cls.query.filter_by(diamond_id=i['diamond_id']).first()
            if issue:
                issue.update(**i)
            else:
                issue = cls.create(**i)
                created = created + 1
        except Exception, err:
            print 'Issue failed creation: ', i.get('complete_title')
            print 'Error: ', err
            db.session.rollback()
            issue = None
        return (issue, created)

    @classmethod
    def check_parent_status(cls, title, issue_number):
        similar_issues = cls.query.filter(
            cls.title == title,
            cls.issue_number == issue_number
        )
        similar_issues = sorted(similar_issues)
        for index, issue in enumerate(similar_issues):
            if index == 0:
                issue.is_parent = True
                if len(similar_issues) > 1:
                    issue.has_alternates = True
            else:
                issue.is_parent = False
                issue.has_alternates = True
            issue.save()
        return

    @staticmethod
    def check_record_relevancy(record, supported_publishers, days):
        if record.get('category') == 'Comics':
            if record.get('publisher') in supported_publishers:
                record_date_string = record.get('prospective_release_date')
                release_date = datetime.strptime(record_date_string, '%Y-%m-%d').date()
                if release_date > (datetime.now().date() - timedelta(days=7)) \
                    and release_date < (datetime.now().date() + timedelta(days=days)):
                    return True
        return False

    @staticmethod
    def check_release_relevancy(record, supported_publishers):
        """
        Strips the publisher string of an asterisk (*) and chesk to see if it is a
        publisher in the supported publishers attribute. Also limits relevency to
        issues with a D or an E in the discount code slot.
        """
        try:
            if record['publisher'].strip('*') in supported_publishers:
                if record['discount_code'] in ['D', 'E']:
                    return True
        except Exception:
            pass
        return False

    @classmethod
    def release_from_raw(cls, record, date):
        if record['diamond_id'][-1:].isalpha():
            diamond_id = record['diamond_id'][:-1]
        else:
            diamond_id = record['diamond_id']

        issue = cls.query.filter_by(diamond_id=diamond_id).first()
        if not issue:
            print 'Issue not found: %s | %s | %s' % (record['diamond_id'],
                                                     record['publisher'],
                                                     record['complete_title'])
        else:
            print 'Releasing: ', issue.complete_title
            issue.on_sale_date = date
            issue.save()
        return issue


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
        return (db.select(
                        [db.func.count(titles_users.c.user_id)
                                .label('num_subscribers')])
                   .where(titles_users.c.title_id == cls.title_id)
                   .label('total_subscribers')
                )

    def to_json(self):
        if self.on_sale_date:
            release_date = self.on_sale_date.strftime('%Y-%m-%d')
        else:
            release_date = None
        if self.has_alternates:
            alternates = [
                    {
                        'complete_title': i.complete_title,
                        'is_parent': i.is_parent,
                        'id': i.id
                    }
                    for i in self.alternates
            ]
        else:
            alternates = []
        i = {
            'id': self.id,
            'complete_title': self.complete_title,
            'publisher': {'id': self.publisher.id,
                          'name': self.publisher.name},
            'title': {'id': self.title.id,
                      'name': self.title.name},
            'other': self.other,
            'price': self.retail_price,
            'diamond_id': self.diamond_id,
            'release_date': release_date,
            'issue_number': self.issue_number,
            'cover_image': self.cover_image.find_thumbnail(width=500).locate(),
            'description': self.description,
            'is_parent': self.is_parent,
            'alternates': alternates
        }
        return i

    def set_cover_image_from_url(self, url, overwrite=False, default=False,
            timeout=5):
        """
        Downloads a jpeg file from a url and stores it in the image store.

        :param issue: :class:`Issue` object class
        :param url: URL to download the jpeg cover image format
        :param overwrite: Boolean flag that overwrites an existing image
        """
        created_flag = False
        try:
            if not self.cover_image.original or overwrite:
                r = requests.get(url, timeout=timeout)
                if r.status_code==200 and r.headers['content-type']=='image/jpeg':
                    with store_context(store):
                        self.cover_image.from_blob(r.content)
                        self.save()
                        self.cover_image.generate_thumbnail(height=600)
                        self.save()
                        created_flag = True
        except Exception, err:
            print 'Exception caught in set_cover_image_from_url', err
        except Timeout:
            print 'The request for the image has timed out!'
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
        image = None
        if self.cover_image:
            with store_context(store):
                try:
                    image = self.cover_image.find_thumbnail(
                                                width=width,
                                                height=height)
                except NoResultFound:
                    image = self.cover_image.generate_thumbnail(
                                                width=width,
                                                height=height)
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
        backref=db.backref('creators', lazy='dynamic'),
        lazy='dynamic'
    )

    @classmethod
    def from_raw(cls, record):
        record = deepcopy(record)
        created = 0
        creators_list = []
        try:
            creators_string = record.get('people')
            people = re.split(';|,', creators_string)
            for person in people:
                person = person.strip()
                creator = cls.query.filter_by(name=person).first()
                if not creator:
                    creator = cls.create(name=person)
                    created = created + 1
                creators_list.append(creator)
        except Exception, err:
            print 'Creator failed creation: ', person
            print 'Error: ', err
            db.session.rollback()
            creators_list = []
        return (creators_list, created)

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

    @classmethod
    def refresh_user_bundle(cls, user, date, matches=None):
        if not matches:
            issues = Issue.query.filter(
                                    Issue.on_sale_date==date,
                                    Issue.is_parent==True)\
                                .all()
            matches = [i for i in issues if i.title in user.pull_list]
        bundle = cls.query.filter(cls.user==user, cls.release_date==date)\
                          .first()
        if bundle:
            bundle.update(issues=matches, last_updated=datetime.now())
        else:
            bundle = cls.create(
                user=user,
                release_date=date,
                issues=matches,
                last_updated=datetime.now()
            )
        return bundle
