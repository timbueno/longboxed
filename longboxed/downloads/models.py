# -*- coding: utf-8 -*-
"""
    longboxed.downloads.models
    ~~~~~~~~~~~~~~~~~~~~~

    Download models
"""
import re

import requests

from datetime import datetime
from hashlib import md5
from StringIO import StringIO

from bs4 import BeautifulSoup
from flask import current_app
from sqlalchemy import func

from ..core import db, CRUDMixin
from ..helpers import unicode_csv_reader, week_handler
from ..models import Issue, Title


diamonds_issues = db.Table('diamonds_issues',
        db.Column('issue_id', db.Integer, db.ForeignKey('issues.id')),
        db.Column('diamonds_id', db.Integer, db.ForeignKey('diamond_lists.id'))
)


class DiamondList(db.Model, CRUDMixin):
    __tablename__ = 'diamond_lists'

    id = db.Column(db.Integer(), primary_key=True)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    date = db.Column(db.Date())
    hash_string = db.Column(db.String(100), unique=True)
    issue_link_time = db.Column(db.DateTime())
    source = db.Column(db.Text())
    revision = db.Column(db.Integer())

    issues = db.relationship(
            'Issue',
            secondary=diamonds_issues,
            backref=db.backref('diamond_lists', lazy='dynamic'),
            lazy='dynamic'
    )

    def __init__(self):
        pass

    def __str__(self):
        dc = self.date_created.strftime('%Y-%m-%d')
        d = self.date.strftime('%Y-%m-%d')
        h = self.hash_string
        return '<DiamondList(date_created=%s, date=%s, hash=%s)>' % (dc, d, h)

    def __repr__(self):
        return self.__str__()

    def download(self, week, affiliate_id=None):
        """
        Gets file containing a list of shippments from Diamond Distributers.
        This file is served from TFAW's servers. Three files are available at
        any given time; thisweek, nextweek, twoweeks. They describe shipments
        pertaining to their respective timeframes.

        :param week: String designating which diamond list to download
                     Options: 'thisweek', 'nextweek', 'twoweeks'
        """
        date = week_handler(week)
        base_url = 'http://www.tfaw.com/intranet/diamondlists_raw.php'
        payload = {
            'mode': week,
            'uid': affiliate_id,
            'show%5B%5D': 'Comics',
            'display': 'text_raw'
        }
        r = requests.get(base_url, params=payload)

        html = BeautifulSoup(r.content)
        self.source = html.pre.string.strip(' \t\n\r')
        self.date = date
        return (self.source, self.date)

    def hash_source(self):
        if self.source == None:
            raise Exception('Source is not set!')
        self.hash_string = md5(self.source).hexdigest()
        return self.hash_string

    def clean_diamond_id(self, diamond_id):
        if diamond_id[-1:].isalpha():
            diamond_id = diamond_id[:-1]
        return diamond_id

    def process_csv(self, fieldnames):
        f = StringIO(self.source)
        reader = unicode_csv_reader(f, fieldnames)
        return [row for row in reader]

    def link_issues(self, fieldnames, supported_publishers, process_failed=True):
        data = self.process_csv(fieldnames)
        issues = []
        failed_rows = []
        for row in data:
            if Issue.check_release_relevancy(row, supported_publishers):
                diamond_id = self.clean_diamond_id(row['diamond_id'])
                issue = Issue.query.filter_by(diamond_id=diamond_id).first()
                if issue:
                    # Issue was found, save for later
                    issues.append(issue)
                else:
                    # Row not found for various reasons, add to list for later
                    # processing
                    failed_rows.append(row)
        if process_failed:
            fixed_issues = self.process_failed_rows(failed_rows, fix_records=True)
        else:
            fixed_issues = []
        issues = issues + fixed_issues
        if issues:
            self.issues = issues
        else:
            self.issues = []
        self.save()
        return self.issues

    def release_issues(self, date_override=None):
        print 'Releasing Issues!'
        date = date_override or self.date
        print '    Date Created: %s' % self.date_created
        print '    Date: %s' % date
        print '    Issues: %i' % self.issues.count()
        print '    Hash: %s' % self.hash_string
        currently_released_issues = Issue.query.filter(
                                                   Issue.on_sale_date==date)\
                                               .all()
        for issue in currently_released_issues:
            issue.on_sale_date = None
            issue.save()
        for issue in self.issues.all():
            issue.on_sale_date = date
            issue.save()

    @classmethod
    def download_and_process(cls, week, fieldnames, supported_publishers):
        d_list = None
        new_list = cls.new()
        source, date = new_list.download(week)
        hash_string = new_list.hash_source()
        old_list = cls.query.filter_by(hash_string=hash_string).first()

        if not old_list:
            print 'Processing a new list!'
            latest_list = cls.query.filter(
                                       cls.date==date)\
                                   .order_by(cls.revision.desc())\
                                   .first()
            if latest_list:
                print 'Earlier lists found!'
                print 'This new revision: %s' % (latest_list.revision + 1)
                new_list.revision = latest_list.revision + 1
            else:
                print 'No earlier revisions'
                new_list.revision = 1
            issues = new_list.link_issues(fieldnames, supported_publishers)
            d_list = new_list.save()
        else:
            print 'Found an old list!'
            print '    Date Created: %s' % old_list.date_created
            print '    Date: %s' % old_list.date
            print '    Issues: %i' % old_list.issues.count()
            print '    Hash: %s' % old_list.hash_string

        return d_list

    def process_failed_rows(self, failed_rows, fix_records=False):
        grouped_rows = {}
        fixed_issues = []
        for row in failed_rows:
            # Parse the complete title row into its base parts.
            # Group the rows together based on like titles and issue numbers
            try:
                m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', row['complete_title']).groupdict()
                matched_tuple = (m['issue_number'], m['title'])
                if matched_tuple in grouped_rows.keys():
                    grouped_rows[matched_tuple].append(row)
                else:
                    grouped_rows[matched_tuple] = [row]
            except Exception, err:
                print err
        # Some diamond list titles just cannot be matched correctly to the database
        # titles. Run them against a mapping between bum titles and their correctly
        # named database titles.
        for key in grouped_rows.keys():
            diamond_list_fixes = current_app.config['DIAMOND_LIST_FIXES']
            if diamond_list_fixes.get(key[1]):
                fixed_name = diamond_list_fixes[key[1]]
                grouped_rows[(key[0], fixed_name)] = grouped_rows.pop(key)
        # Process the grouped rows. Search the database based on the grouped title
        # and the associated issue number.
        for key in grouped_rows.keys():
            query_string = '%'+key[1].replace(' ', '%%')+'%'
            issues = Issue.query\
                          .filter(Issue.issue_number==key[0])\
                          .join(Title.issues)\
                          .filter(Title.name.ilike(query_string))\
                          .order_by(func.char_length(Issue.complete_title))\
                          .all()
            if issues:
                rows = grouped_rows[key]
                rows.sort(key=lambda row: len(row['complete_title']), reverse=False)
                numeric_issues = []
                for issue in issues:
                    if issue.diamond_id.isnumeric():
                        numeric_issues.append(issue)
                for i, issue in enumerate(numeric_issues):
                    if i > (len(rows)-1):
                        break
                    print 'ID: %s | DB: %s | DL: %s' % (rows[i]['diamond_id'],
                                                      issue.complete_title,
                                                      rows[i]['complete_title'])
                    if fix_records:
                        issue.diamond_id = rows[i]['diamond_id']
                        issue.save()
                    fixed_issues.append(issue)
            else:
                pass
                #rows = grouped_rows[key]
                #for row in rows:
                    #print 'Failed Issues: %s | %s' % (row['complete_title'],
                                                      #row['publisher'])
        return fixed_issues

