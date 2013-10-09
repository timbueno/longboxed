# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import csv
from StringIO import StringIO

from flask.ext.script import Command, Option, prompt, prompt_bool

# from ..core import db
from ..helpers import current_wednesday, mail_content, two_wednesdays, next_wednesday
from ..importer import DailyDownloadRecord
from ..services import comics


class TestCommand(Command):
    def run(self):
        record = {
            'status': 'instock',
            'last_updated': '2013-10-07 07:00:22',
            'people': 'Brian Azzarello;Eduardo Risso;Dave Johnson',
            'isbn': '1401222870',
            'category': 'Comics',
            'big_image': 'http://affimg.tfaw.com/covers_tfaw/400/ap/apr090260d.jpg',
            'merchant_id': '8908',
            'theme': '100 Bullets',
            'short_description': '',
            'thumbnail': 'http://affimg.tfaw.com/covers_tfaw/100/ap/apr090260d.jpg',
            'merchant': 'Things From Another World',
            'complete_title': 'Fantomex Max #1 (of 4)',
            'description': 'This is a pretty sweet description of the issue',
            'price': '17.99',
            'merchant_subcategory': '',
            'a_link': 'http://www.shareasale.com/m-pr.cfm?merchantID=8908&userID=YOURUSERID&productID=466299720',
            'genre': 'Crime',
            'sas_category': 'Books/Reading',
            'retail_price': '2.99',
            'diamond_id': 'APR090260D',
            'publisher': 'DC Comics',
            'popularity': '0',
            'upc': '978140122287151999',
            'sas_subcategory': 'Misc.',
            'current_tfaw_release_date': '2013-10-09'
        }
        csv_rules = [
            (0, 'ProductID', 'product_id', True),
            (1, 'Name', 'complete_title', True),
            (2, 'MerchantID', 'merchant_id', False),
            (3, 'Merchant', 'merchant', False),
            (4, 'Link', 'a_link', True),
            (5, 'Thumbnail', 'thumbnail', True),
            (6, 'BigImage', 'big_image', True),
            (7, 'Price', 'price', False),
            (8, 'RetailPrice', 'retail_price', True),
            (9, 'Category', 'sas_category', False),
            (10, 'SubCategory', 'sas_subcategory', False),
            (11, 'Description', 'description', True),
            (12, 'OnSaleDate', 'current_tfaw_release_date', True),
            (13, 'Genre', 'genre', True),
            (14, 'People', 'people', True),
            (15, 'Theme', 'theme', False),
            (16, 'Popularity', 'popularity', True),
            (17, 'LastUpdated', 'last_updated', True),
            (18, 'status', 'status', False),
            (19, 'manufacturer', 'publisher', True),
            (20, 'partnumber', 'diamond_id', True),
            (21, 'merchantCategory', 'category', True),
            (22, 'merchantSubcategory', 'merchant_subcategory', False),
            (23, 'shortDescription', 'short_description', False),
            (24, 'ISBN', 'isbn', False),
            (25, 'UPC', 'upc', True)
        ]
        csv_rules = {x[2]: x[3] for x in csv_rules}
        my_record = DailyDownloadRecord('782419', record, csv_rules)
        my_record.run()


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
            date = two_wednesdays()
            raise NotImplementedError
        content = comics.get_shipping_from_TFAW(week)
        shipping = comics.get_issue_dict_shipping(content)
        diamond_ids = [x['ITEMCODE'] for x in shipping]
        comics.compare_shipping_with_database(diamond_ids, date)
        print 'Done Scheduling'