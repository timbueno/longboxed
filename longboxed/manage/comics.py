# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import csv


from flask import current_app as app
from flask.ext.script import Command

from bs4 import BeautifulSoup
from StringIO import StringIO
import requests

from ..services import comics

publisher_names = ['IMAGE COMICS', 'DARK HORSE COMICS', 'MARVEL COMICS', \
                   'DC COMICS', 'ARCHIE COMIC PUBLICATIONS', 'IDEA & DESIGN WORKS LLC', \
                   'DYNAMIC FORCES', 'BOOM ENTERTAINMENT']

def get_shipping_this_week():
    base_url = 'http://www.tfaw.com/intranet/diamondlists_raw.php'
    payload = {
        'mode': 'thisweek',
        'uid': app.config['AFFILIATE_ID'],
        'show%5B%5D': 'Comics',
        'display': 'text_raw'
    }
    r = requests.get(base_url, params=payload)
    return r.content


def get_issues_shipping(raw_content):
    html = BeautifulSoup(raw_content)
    f = StringIO(html.pre.string.strip(' \t\n\r'))
    incsv = csv.DictReader(f)
    shipping = [x for x in incsv if check_publisher(x['Vendor'])]
    return shipping

def check_publisher(publisher):
    try:
        if publisher.strip('*') in publisher_names:
            return True
        else:
            return False
    except:
        return False

def parse_releases(raw_data):
    pass


class CrossCheckCommand(Command):
    """Cross checks releases with items in database"""
    
    def run(self):
        content = get_shipping_this_week()
        shipping = get_issues_shipping(content)
        not_in_db = [i for i in shipping if not comics.issues.first(diamond_id=(i['ITEMCODE']+i['DiscountCode']))]
        for i in not_in_db:
            print '%s    %s' % (i['ITEMCODE']+i['DiscountCode'], i['TITLE'])
        return


class UpdateDatabaseCommand(Command):
    """Updates database with TFAW Daily Download"""

    def run(self):
        print 'Starting update'
        comics.add_new_issues_to_database()
        print 'Done Adding to DB'


class ScheduleReleasesCommand(Command):
    """Automatically schedule releases from Diamond Release file"""
    
    def run(self):
        print 'Starting scheduling'
        content = comics.get_shipping_this_week()
        shipping = comics.get_diamond_ids_shipping(content)
        comics.compare_shipping_with_database(shipping)
        print 'Done Scheduling'