# -*- coding: utf-8 -*-
"""
    longboxed.importer
    ~~~~~~~~~~~~~~~

    NewDailyDownloadImporter creates issues, titles, and publishers from
    TFAW's database CSV file.

    NewWeeklyReleasesImporter sets the 'on_sale_date' attribute of issue models
    based on Diamond Lists recieved from TFAW.
"""

from csv import DictReader
from datetime import datetime
from gzip import GzipFile
from logging import getLogger
from StringIO import StringIO

import requests

from bs4 import BeautifulSoup

from .helpers import week_handler, unicode_csv_reader
from .models import Issue, Title, Publisher, Creator


process_logger = getLogger('issue_processing')


class NewDailyDownloadImporter(object):
    """
    Imports the daily download from TFAW
    """
    def __init__(self):
        pass

    def run(self, csv_fieldnames, supported_publishers, affiliate_id, thumbnail_widths, days=7):
        content = self.download(affiliate_id)
        data = self.load(content, csv_fieldnames)
        issues = self.process(data, supported_publishers, days, affiliate_id, thumbnail_widths)
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

    def process(self, data, supported_publishers, days, affiliate_id, thumbnail_widths):
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

                        issue.set_cover_image_from_url(issue.big_image)
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


class NewWeeklyReleasesImporter(object):
    """
    Processes releases
    """
    def __init__(self):
        pass

    def run(self, csv_fieldnames, supported_publishers, affiliate_id, week='thisweek'):
        print 'Setting Date'
        date = week_handler(week)
        print date
        print 'Getting Content'
        content = self.download(week, affiliate_id)
        print 'Loading Data'
        data = self.load(content, csv_fieldnames)
        print 'Releasing Issues'
        self.process(data, supported_publishers, date)
        return


    def download(self, week, affiliate_id):
        """
        Gets file containing a list of shippments from Diamond Distributers.
        This file is served from TFAW's servers. Three files are available at
        any given time; thisweek, nextweek, twoweeks. They describe shipments
        pertaining to their respective timeframes.

        :param week: String designating which diamond list to download
                     Options: 'thisweek', 'nextweek', 'twoweeks'
        """
        if week not in ['thisweek', 'nextweek', 'twoweeks']:
            raise Exception('Not a valid input for week selection')
        base_url = 'http://www.tfaw.com/intranet/diamondlists_raw.php'
        payload = {
            'mode': week,
            'uid': affiliate_id,
            'show%5B%5D': 'Comics',
            'display': 'text_raw'
        }
        r = requests.get(base_url, params=payload)

        return r.content

    def load(self, content, fieldnames):
        """
        Turns returned content from a request for a Diamond list into someting
        we can work with. It discards any items that do not have a vender matching
        a vender in 'SUPPORTED_DIAMOND_PUBS' settings variable. It also discards any
        item whose discount code is not a D or and E.

        :param raw_content: html content returned from TFAWs servers, diamond list
        """
        html = BeautifulSoup(content)
        f = StringIO(html.pre.string.strip(' \t\n\r'))
        reader = unicode_csv_reader(f, fieldnames=fieldnames)
        data = [row for row in reader]
        return data

    def process(self, data, supported_publishers, date):
        issues = []
        already_scheduled = Issue.query.filter_by(on_sale_date=date).all()
        for issue in already_scheduled:
            issue.on_sale_date = None
            issue.save()
        for row in data:
            if Issue.check_release_relevancy(row, supported_publishers):
                issue = Issue.release_from_raw(row, date)
                issues.append(issue)
        return issues


if __name__ == "__main__":
    print 'WHOOPS!'
