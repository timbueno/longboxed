# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import csv
from pprint import pprint
from StringIO import StringIO

from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool

from ..helpers import mail_content
from ..importer import DailyDownloadImporter, DailyDownloadRecord, WeeklyReleasesImporter, WeeklyReleaseRecord
from ..services import comics, bundle


class TestCommand(Command):
    def run(self):
        pass

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
        issue = comics.issues.first(diamond_id=diamond_id)
        if issue:
            url = prompt('Url of jpg image for cover image')
            overwrite = False
            if issue.cover_image.original:
                print 'Issue object already has a cover image set.'
                overwrite = prompt_bool('Overwrite existing picture?')
            success = comics.issues.set_cover_image_from_url(issue, url, overwrite)
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


# class ScheduleReleasesCommand(Command):
#     """Automatically schedule releases from Diamond Release file"""
    
#     def get_options(self):
#         return [
#             Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
#         ]

#     def run(self, week):
#         print 'Starting scheduling'
#         if week == 'thisweek':
#             date = current_wednesday()
#         if week == 'nextweek':
#             date = next_wednesday()
#         if week == 'twoweeks':
#             date = two_wednesdays()
#             raise NotImplementedError
#         content = comics.get_shipping_from_TFAW(week)
#         shipping = comics.get_issue_dict_shipping(content)
#         diamond_ids = [x['ITEMCODE'] for x in shipping]
#         comics.compare_shipping_with_database(diamond_ids, date)
#         print 'Done Scheduling'