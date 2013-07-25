from mongoengine import *
from bs4 import UnicodeDammit
from datetime import datetime

from settings import MONGODB_SETTINGS as mdbs
# from comics.models import Comic

import csv
import gzip
import re
import requests
import sys


AFFILIATE_ID = 782419
DD_FILE = 'dd.gz'

class Comic(Document):
    meta = {'collection': 'comics_test'}
    productID = StringField()
    name = StringField()
    issue_number = FloatField()
    issues = FloatField()
    other = ListField(StringField())
    complete_title = StringField()
    one_shot = BooleanField()
    alink = StringField()
    thumbnail = StringField()
    bigImage = StringField()
    retailPrice = FloatField()
    description = StringField()
    onSaleDate = DateTimeField()
    genre = StringField()
    people = ListField(StringField())
    popularity = FloatField()
    lastUpdated = DateTimeField()
    publisher = StringField()
    diamondid = StringField()
    category = StringField()
    upc = StringField()

def daily_download():
    print 'Downloading Daily Download'
    # daily download url and affiliate id params
    base_url = 'http://www.tfaw.com/intranet/download-8908-daily.php'
    payload = {
        'aid': AFFILIATE_ID,
        't': '',
        'z': 'gz'
    }
    # Download the file
    r = requests.get(base_url, params=payload)
    with open(DD_FILE, 'wb') as code:
        code.write(r.content)
    print '...Done'
    return


def get_comics():
    print 'Checking for comics'
    # open gzip archive and extract only comics
    with gzip.open(DD_FILE, 'rb') as f:
        comics = []
        reader = csv.reader(f, delimiter='|')
        for item in reader:
            if item[-5] == 'Comics':
                item = [UnicodeDammit(element).unicode_markup for element in item]
                comics.append(item)
    print '...Done'
    return comics


def title_info(title):
    try:
        # Try a basic matching technique
        m = re.match(r'(?P<name>[^#]*[^#\s])\s*(?:#(?P<issue_number>(\d+))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', title).groupdict()
        # Convert issue numbers to floats
        if is_float(m['issue_number']):
            m['issue_number'] = float(m['issue_number'])
        if is_float(m['issues']):
            m['issues'] = float(m['issues'])
        m['one_shot'] = False
        other = [m['other']]
        # Handle multiple parenthesis matches
        if '' in other and len(other) == 1:
            other = [] # Make a fresh list
            # m['other'] = None # For consistancy
            n = re.findall(r'\s*(\(.*?\))',m['name']) # Find all parenthesis groups
            # Add all groups to other list
            if n:
                # other = []
                for match in n:
                    m['name'] = m['name'].replace(match, '')
                    other.append(match)
                m['name'] = m['name'].strip() # Clean up the name
                m['other'] = other
        if m['name'].find('One Shot') != -1:
            # Set 'One Shot' flag
            m['one_shot'] = True
            # Remove 'One Shot' from name
            m['name'] = m['name'].replace('One Shot', '')
        m['other'] = other
    except:
        print "Unexpected error:", sys.exc_info()[3]
    finally:
        m['complete_title'] = unicode(title)
    return m


def is_float(number):
    try: 
        float(number)
        return True
    except (ValueError, TypeError):
        return False


# 'info': { #1
#     'name': unicode,
#     'issue_number': float,
#     'issues': float,
#     'other': unicode,
#     'complete_title': unicode,
#     'one_shot': bool
# },

def add_comics_to_mongo():
    daily_download()
    comics = get_comics()

    connect(mdbs['DB'], username=mdbs['USERNAME'], password=mdbs['PASSWORD'],
            host=mdbs['HOST'], port=mdbs['PORT'])

    for i, comic in enumerate(comics):
        try:
            new = Comic()
            new.productID = comic[0]
            # Extract Title Info
            t_info = title_info(comic[1])
            new.name = t_info['name']
            new.issue_number = t_info['issue_number']
            new.issues = t_info['issues']
            new.other = t_info['other']
            new.complete_title = t_info['complete_title']
            new.one_shot = t_info['one_shot']
            new.alink = re.sub('YOURUSERID', unicode(AFFILIATE_ID), comic[4])
            new.thumbnail = comic[5]
            new.bigImage = comic[6]
            new.retailPrice = float(comic[8]) if is_float(comic[8]) else None
            new.description = comic[11]
            try:
                new.onSaleDate = datetime.strptime(comic[12], '%Y-%m-%d')
            except:
                new.onSaleDate = None
            new.genre = comic[13]
            new.people = comic[14].split(';')
            new.popularity = float(comic[16]) if is_float(comic[16]) else None
            try:
                new.lastUpdated = datetime.strptime(comic[17], '%Y-%m-%d %H:%M:%S')
            except:
                new.lastUpdated = None
            new.publisher = comic[19]
            new.diamondid = comic[20]
            new.category = comic[21]
            new.upc = comic[25]
            new.save()
        except:
            print 'SOMETHING HAPPENED', comic
            print "Unexpected error:", sys.exc_info()[1]

        if i % 250 == 0:
            print 'Saved %d / %d comics' % (i, len(comics))


if __name__ == "__main__":
    add_comics_to_mongo()