# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import csv

from flask.ext.script import Command, Option

from StringIO import StringIO

from ..helpers import current_wednesday, mail_content, next_wednesday
from ..services import comics


class CrossCheckCommand(Command):
    """
    Cross checks releases with items in database and mails missing
    issues to a provided email address
    """
    
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
            Option('-e', '--email', dest='email', default='timbueno@gmail')
        ]

    def run(self, email, week):
        content = comics.get_shipping_from_TFAW(week)
        shipping = comics.get_issue_dict_shipping(content)
        not_in_db = [i for i in shipping if not comics.issues.first(diamond_id=(i['ITEMCODE']+i['DiscountCode']))]
        not_in_db = sorted(not_in_db, key=lambda x: x['Vendor'])
        f = StringIO()
        ordered_fieldnames = ['ITEMCODE', 'DiscountCode', 'TITLE', 'Vendor', 'PRICE']
        outcsv = csv.DictWriter(f, fieldnames=ordered_fieldnames, delimiter='\t')
        for i in not_in_db:
            outcsv.writerow(i)
        mail_content([email], 'checker@longboxed.com', 'Attached is your checks', f.getvalue())
        f.close()
        return


class UpdateDatabaseCommand(Command):
    """Updates database with TFAW Daily Download"""

    def run(self):
        print 'Starting update'
        comics.add_new_issues_to_database()
        print 'Done Adding to DB'


class ScheduleReleasesCommand(Command):
    """Automatically schedule releases from Diamond Release file"""
    
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        print 'Starting scheduling'
        if week == 'thisweek':
            date = current_wednesday()
        if week == 'nextweek':
            date = next_wednesday()
        if week == 'twoweeks':
            raise NotImplementedError
        content = comics.get_shipping_from_TFAW(week)
        shipping = comics.get_issue_dict_shipping(content)
        diamond_ids = [x['ITEMCODE']+x['DiscountCode'] for x in shipping]
        comics.compare_shipping_with_database(diamond_ids, date)
        print 'Done Scheduling'