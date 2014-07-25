# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import csv
from datetime import datetime
from StringIO import StringIO
from gzip import GzipFile
from csv import DictReader
from copy import deepcopy

import requests

from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool

from ..helpers import mail_content
from ..importer import DailyDownloadImporter, DailyDownloadRecord, WeeklyReleasesImporter, WeeklyReleaseRecord
from ..services import comics
from ..models import Creator, Issue, Title, Publisher


class TestCommand(Command):
    def run(self):
        base_url = 'http://www.tfaw.com/intranet/download-8908-daily.php'
        payload = {
            'aid': current_app.config['AFFILIATE_ID'],
            't': '',
            'z': 'gz'
        }
        r = requests.get(base_url, params=payload)

        fieldnames = [x[2] for x in current_app.config['CSV_RULES']]
        with GzipFile(fileobj=StringIO(r.content)) as f:
            reader = DictReader(f, fieldnames=fieldnames, delimiter='|')
            data = [row for row in reader]

        try:
            new_publishers = 0
            new_titles = 0
            new_issues = 0
            new_creators = 0

            for record in data:
                if Issue.check_record_relevancy(record, current_app.config['SUPPORTED_PUBS'], 7):
                    # Attempt to create new models from raw records
                    publisher, publishers_created = Publisher.from_raw(record)
                    title, titles_created = Title.from_raw(record)
                    issue, issues_created = Issue.from_raw(record)
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
                        Issue.check_parent_status(issue.title, issue.issue_number)
        except Exception:
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

        return
        

class ScheduleReleasesCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        release_instance = WeeklyReleasesImporter(
            week=week,
            affiliate_id=current_app.config['AFFILIATE_ID'],
            supported_publishers=current_app.config['SUPPORTED_DIAMOND_PUBS'],
            csv_rules=current_app.config['RELEASE_CSV_RULES'],
            record=WeeklyReleaseRecord
        )
        scheduled_releases = release_instance.run()
        return

class ImportDatabase(Command):
    def get_options(self):
        return [
            Option('--days', '-d', dest='days', default=21, type=int)
        ]

    def run(self, days):
        print 'Importing the next %d days worth of comic books...' % days
        import_instance = DailyDownloadImporter(
            days=days,
            affiliate_id=current_app.config['AFFILIATE_ID'],
            supported_publishers=current_app.config['SUPPORTED_PUBS'],
            csv_rules=current_app.config['CSV_RULES'],
            record=DailyDownloadRecord
        )
        imported_issues = import_instance.run()
        return


class SetCoverImageCommand(Command):
    """
    Sets the cover image of an issue. The issues is found in the 
    database with a diamond id. If the issue already has an image
    attached, you can optionally choose to replace it.
    """
    def run(self):
        diamond_id = prompt('Issue Diamond id')
        # issue = comics.issues.first(diamond_id=diamond_id)
        issue = Issue.query.filter_by(diamond_id=diamond_id).first()
        if issue:
            url = prompt('Url of jpg image for cover image')
            overwrite = False
            if issue.cover_image.original:
                print 'Issue object already has a cover image set.'
                overwrite = prompt_bool('Overwrite existing picture?')
            # success = comics.issues.set_cover_image_from_url(issue, url, overwrite)
            success = issue.set_cover_image_from_url(url, overwrite=overwrite)
            if success:
                print 'Successfully set cover image'
            return
        print 'No issue found!'
        return



class CrossCheckCommand(Command):
    """
    Cross checks releases with items in database and mails missing
    issues to a provided email address
    """
    
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
            Option('-e', '--email', dest='email', default='timbueno@gmail.com')
        ]

    def run(self, email, week):
        if week == 'twoweeks':
            raise NotImplementedError
        content = comics.get_shipping_from_TFAW(week)
        shipping = comics.get_issue_dict_shipping(content)
        not_in_db = [i for i in shipping if not comics.issues.first(diamond_id=i['ITEMCODE'])]
        not_in_db = sorted(not_in_db, key=lambda x: x['Vendor'])
        f = StringIO()
        ordered_fieldnames = ['ITEMCODE', 'DiscountCode', 'TITLE', 'Vendor', 'PRICE']
        outcsv = csv.DictWriter(f, fieldnames=ordered_fieldnames, delimiter='\t')
        for i in not_in_db:
            outcsv.writerow(i)
        mail_content([email], 'checker@longboxed.com', 'Testing', 'Attached is your checks', f.getvalue())
        f.close()
        return


class UpdateDatabaseCommand(Command):
    """Updates database with TFAW Daily Download"""

    def get_options(self):
        return [
            Option('-d','--days', dest='days', required=True)
        ]

    def run(self, days):
        print 'Starting update'
        days = int(days)
        comics.add_new_issues_to_database(days=days)
        print 'Done Adding to DB'