# -*- coding: utf-8 -*-
"""
    longboxed.importer
    ~~~~~~~~~~~~~~~

    DailyDownloadImporter creates issues, titles, and publishers from
    TFAW's database CSV file.

"""
from csv import DictReader
from datetime import datetime
from gzip import GzipFile
from logging import getLogger
from StringIO import StringIO

import requests

from .models import Issue, Title, Publisher, Creator


process_logger = getLogger('issue_processing')


class DailyDownloadImporter(object):
    """
    Imports the daily download from TFAW
    """
    def __init__(self):
        pass

    def run(self, csv_fieldnames, supported_publishers, affiliate_id,
            thumbnail_widths, days=7, comparison_image=None):
        content = self.download(affiliate_id)
        data = self.load(content, csv_fieldnames)
        issues = self.process(data, supported_publishers, days,
                              affiliate_id, thumbnail_widths,
                              comparison_image)
        return issues

    def download(self, affiliate_id):
        base_url = 'http://www.tfaw.com/intranet/download-8908-daily.php'
        payload = {
            'aid': affiliate_id,
            't': '',
            'z': 'gz'
        }
        r = requests.get(base_url, params=payload)
        return r.content

    def load(self, content, csv_fieldnames):
        with GzipFile(fileobj=StringIO(content)) as f:
            reader = DictReader(f, fieldnames=csv_fieldnames, delimiter='|')
            data = [row for row in reader]
        return data

    def process(self, data, supported_publishers, days, affiliate_id,
            thumbnail_widths, comparison_image):
        try:
            new_publishers = 0
            new_titles = 0
            new_issues = 0
            new_creators = 0

            for record in data:
                if Issue.check_record_relevancy(record, supported_publishers, days):
                    # Attempt to create new models from raw records
                    publisher, publishers_created = Publisher.from_raw(record)
                    title, titles_created = Title.from_raw(record)
                    issue, issues_created = Issue.from_raw(record, affiliate_id)
                    creators, creators_created = Creator.from_raw(record)

                    # Update newly created model counts
                    new_publishers = new_publishers + publishers_created
                    new_titles = new_titles + titles_created
                    new_issues = new_issues + issues_created
                    new_creators = new_creators + creators_created

                    if titles_created and publisher:
                        title.publisher = publisher
                        title.save()

                    if issue:
                        issue.title = title
                        issue.publisher = publisher
                        issue.creators = creators
                        issue.save()

                        issue.set_cover_image_from_url(
                                issue.big_image,
                                comparison=comparison_image)
                        for width in thumbnail_widths:
                            issue.find_or_create_thumbnail(width)
                        Issue.check_parent_status(issue.title, issue.issue_number)
        except Exception, err:
            ####### PUT SOMETHING HERE
            print 'Something Happened!!!!', err
            print record
        finally:
            summary = """
            ~~~~~~~~~~~~~~~~~~~~~~~~
            Database Update Report
            Time: %s
            ~~~~~~~~~~~~~~~~~~~~~~~~
            Created Issues:     %d
            Created Titles:     %d
            Created Publishers: %d
            ~~~~~~~~~~~~~~~~~~~~~~~~
            Issues in DB:       %d
            ~~~~~~~~~~~~~~~~~~~~~~~~""" % (datetime.now(), new_issues, \
                                           new_titles, \
                                           new_publishers, \
                                           Issue.query.count()
                                          )
            print summary

        return True


if __name__ == "__main__":
    print 'WHOOPS!'
