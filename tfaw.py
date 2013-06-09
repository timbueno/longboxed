from mongokit import Connection, Document
from bs4 import UnicodeDammit
from datetime import datetime

import csv
import gzip
import re
import requests
import sys

from models import Comic

AFFILIATE_ID = 782419
DD_FILE = 'dd.gz'

# MongoLab configuration
MONGO_USERNAME = 'bueno'
MONGO_PASSWORD = 'Cry9Gas'
MONGO_DBNAME = 'thisweekscomics'
MONGO_HOST = 'ds031877.mongolab.com'
MONGO_PORT = 31877
MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (MONGO_USERNAME, MONGO_PASSWORD,
                                          MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

def open_connection():
    print 'Opening connection...'
    mongo = Connection(MONGO_URI)
    mongo.register(Comic)
    collection = mongo[MONGO_DBNAME]
    print '...Done'
    return collection

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
        m = re.match(r'(?P<name>[^#]*[^#\s])\s*(?:#(?P<issue_number>(\d+))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', title).groupdict()
        if is_float(m['issue_number']):
            m['issue_number'] = float(m['issue_number'])
        if is_float(m['issues']):
            m['issues'] = float(m['issues'])
    except:
        'PROBLEM IN TITLE_INFO'
    finally:
        m['complete_title'] = unicode(title)
    return m

def is_float(number):
    try: 
        float(number)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    daily_download()
    comics = get_comics()
    collection = open_connection()

    cList = []
    for i, comic in enumerate(comics):
        try:
            new = Comic()
            new.productID = comic[0]
            new.info = title_info(comic[1])
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
            new.id = comic[20]
            new.category = comic[21]
            new.upc = comic[25]
            cList.append(new)
        except:
            print 'SOMETHING HAPPENED', comic
            print "Unexpected error:", sys.exc_info()[1]

        if i % 250 == 0:
            print 'Saved %d / %d comics' % (i, len(comics))

    print cList[0].info
    for i, issue in enumerate(cList):
        collection.comics.update({'id': issue.id}, issue, upsert=True)
        if i % 250 == 0:
            print 'Inserted %d / %d' % (i, len(cList))

# +++++++++++++++++++++++++++++++++++++++++++++++
    # for i, comic in enumerate(comics):
    #     try:
    #         new = collection.test_comics.Comic()
    #         new.productID = comic[0]
    #         new.name = comic[1]
    #         new.alink = comic[4]
    #         new.thumbnail = comic[5]
    #         new.bigImage = comic[6]
    #         new.retailPrice = float(comic[8]) if is_float(comic[8]) else None
    #         new.description = comic[11]
    #         try:
    #             new.onSaleDate = datetime.strptime(comic[12], '%Y-%m-%d')
    #         except:
    #             new.onSaleDate = None
    #         new.genre = comic[13]
    #         new.people = comic[14]
    #         new.popularity = float(comic[16]) if is_float(comic[16]) else None
    #         try:
    #             new.lastUpdated = datetime.strptime(comic[17], '%Y-%m-%d %H:%M:%S')
    #         except:
    #             new.lastUpdated = None
    #         new.publisher = comic[19]
    #         new.diamondID = comic[20]
    #         new.category = comic[21]
    #         new.upc = comic[25]
    #         new.save()
    #     except:
    #         print 'SOMETHING HAPPENED', comic
    #         print "Unexpected error:", sys.exc_info()[1]

    #     if i % 250 == 0:
    #         print 'Saved %d / %d comics' % (i, len(comics))

