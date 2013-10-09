import gzip
import inspect
import re

from copy import deepcopy
from csv import DictReader
from datetime import datetime
from decimal import Decimal
from HTMLParser import HTMLParser

import requests

from flask import current_app

from .services import comics as _comics

class BaseImporter(object):
    """
    Base csv importer class
    """
    def __init__(self, csv_rules, record, delimiter='|', filename='latest_db.gz'):
        self.delimiter = delimiter
        self.filename = filename
        self.record = record
        self.csv_rules = csv_rules
        self.raw_data = []
        self.processed_data = []

    def load(self):
        fieldnames = [x[2] for x in self.csv_rules]
        with gzip.open(self.filename, 'rb') as f:
            reader = DictReader(f, fieldnames=fieldnames, delimiter=self.delimiter)
            self.raw_data = [row for row in reader]
        return self.raw_data

    def download(self):
        raise NotImplementedError


class DailyDownloadImporter(BaseImporter):
    """
    Imports the daily download from TFAW
    """
    def __init__(self, *args, **kwargs):
        super(DailyDownloadImporter, self).__init__(*args, **kwargs)

    def download(self):
        """
        Gets latest Daily Download file from TFAW's servers. This file
        contains a record of every item they have for sale.
        """
        base_url = 'http://www.tfaw.com/intranet/download-8908-daily.php'
        payload = {
            'aid': self.affiliate_id,
            't': '',
            'z': 'gz'
        }
        # Download the file
        r = requests.get(base_url, params=payload)
        with open(self.filename, 'wb') as code:
            code.write(r.content)
        return


class BaseRecord(object):
    """
    Base record class
    """
    def __init__(self, raw_record, csv_rules, pre_process_tag='pre', post_process_tag='post'):
        self.raw_record = raw_record
        self.csv_rules = csv_rules
        self.pre_processes = self.get_processors(pre_process_tag)
        self.post_processes = self.get_processors(post_process_tag)
        self.processed_record = None
        self.object = None

    def get_processors(self, tag):
        processors = [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod) \
            if tag in x[0] and x[0] and x[0] not in ['pre_process', 'post_process', 'get_processors']]
        return processors

    def pre_process(self):
        temp = deepcopy(self.raw_record)
        temp = {key: temp[key] for key in temp.keys() if self.csv_rules[key]}
        for method in self.pre_processes:
            result = getattr(self, method)(temp)
            temp.update(result)
        self.processed_record = temp
        return self.processed_record

    def post_process(self):
        results = {}
        for method in self.post_processes:
            result = getattr(self, method)(self.object)
            results[method] = result
        return results

    def make_object(self):
        raise NotImplementedError

    def run(self):
        try:
            self.pre_process()
            self.make_object()
            self.post_process()
        except NotImplementedError:
            pass

    def is_relevent(self):
        return True


class DailyDownloadRecord(BaseRecord):
    """
    Represents a single record in the daily download
    """
    def __init__(self, affiliate_id, *args, **kwargs):
        super(DailyDownloadRecord, self).__init__(*args, **kwargs)
        self.affiliate_id = affiliate_id

    def is_relevent(self):
        if self.raw_record['category'] == 'Comics' \
            and self.raw_record['publisher'] in current_app.config['SUPPORTED_PUBS']:
            return True
        return False

    def make_object(self):
        if not self.processed_record:
            raise Exception
        issue_dict = deepcopy(self.processed_record)
        publisher = _comics.insert_publisher(
            raw_publisher = issue_dict['publisher']
        )
        title = _comics.insert_title(
            raw_title = issue_dict['title'],
            publisher_object = publisher
        )
        issue = _comics.insert_issue(
            raw_issue_dict = issue_dict,
            title_object = title,
            publisher_object = publisher
        )
        self.object = issue
        return self.object

    def is_float(self, number):
        try: 
            float(number)
            return True
        except (ValueError, TypeError):
            return False

    def pre_complete_title(self, record, key='complete_title'):
        """
        Parses the Title, Issue Number, Total Number of Issues, and other
        information from a title string.

        Example Raw Title String: Infinity Hunt #2 (of 4)

        :param record: String containing raw title.
        :param key: Dictionary key associated with raw unprocessed title
        """
        try:
            # m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>(\d+))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', title).groupdict()
            m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', record[key]).groupdict()
            m['complete_title'] = record[key]
            if m['issue_number']:
                m['issue_number'] = Decimal(m['issue_number'])
            if m['issues']:
                m['issues'] = Decimal(m['issues'])
        except (AttributeError, TypeError):
            m = None
        return m

    def pre_retail_price(self, record, key='retail_price'):
        result = float(record[key]) if self.is_float(record[key]) else None
        return {key: result}

    def pre_a_link(self, record, key='a_link'):
        result = record[key].replace('YOURUSERID', self.affiliate_id)
        return {key: result}

    def pre_diamond_id(self, record, key='diamond_id'):
        if record[key][-1:].isalpha():
            diamond_id = record[key][:-1]
            discount_code = record[key][-1:]
        else:
            diamond_id = record[key]
            discount_code = None
        return {key: diamond_id, 'discount_code': discount_code}

    def pre_description(self, record, key='description'):
        result = HTMLParser().unescape(record[key])
        return {key: result}

    def pre_current_tfaw_release_date(self, record, key='current_tfaw_release_date'):
        result = datetime.strptime(record[key], '%Y-%m-%d').date()
        return {key: result}

    def pre_last_updated(self, record, key='last_updated'):
        result = datetime.strptime(record[key], '%Y-%m-%d %H:%M:%S')
        return {key: result}

    def post_check_parent_status(self, issue):
        similar_issues = _comics.issues.filter(
            _comics.issues.__model__.title == issue.title,
            _comics.issues.__model__.issue_number==issue.issue_number,
            _comics.issues.__model__.diamond_id != issue.diamond_id
        )
        print similar_issues

    def post_cover_image(self, issue):
        created = _comics.issues.set_cover_image_from_url(issue, issue.big_image)
        return created

if __name__ == "__main__":
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
        'product_id': '466299720',
        'popularity': '0',
        'upc': '978140122287151999',
        'sas_subcategory': 'Misc.',
        'current_tfaw_release_date': '2013-10-09'
    }
    csv_rules = {x[2]: x[3] for x in csv_rules}
    my_record = DailyDownloadRecord('782419', record, csv_rules)
    record = my_record.pre_process()
    print record
    # print my_record.is_relevent()

