import inspect
import re

from copy import deepcopy
from csv import DictReader
from datetime import datetime, timedelta
from decimal import Decimal
from functools import wraps
from gzip import GzipFile
from HTMLParser import HTMLParser
from StringIO import StringIO

import requests

from bs4 import BeautifulSoup
from flask import current_app

from .helpers import current_wednesday, two_wednesdays, next_wednesday
from .services import comics as _comics


class BaseImporter(object):
    """
    Base csv importer class
    """
    def __init__(self, csv_rules, record, delimiter='|'):
        self.delimiter = delimiter
        self.record = record
        self.csv_rules = csv_rules
        self.raw_data = []
        self.processed_data = []

    def run(self):
        print 'Beginning process: ', datetime.now()
        content = self.download()
        self.raw_data = self.load(content)
        self.processed_data = self.process(self.raw_data)
        print 'Process Complete: ', datetime.now()
        return self.processed_data

    def download(self):
        raise NotImplementedError

    def load(self, content):
        raise NotImplementedError

    def process(self, raw_content_dict):
        raise NotImplementedError


def daily_download_report(fn):
    @wraps(fn)
    def wrapper(self, raw_data):
        now = datetime.now()
        issue_count = _comics.issues.count()
        title_count = _comics.titles.count()
        publisher_count = _comics.publishers.count()
        data = fn(self, raw_data)
        print '~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Database Update Report'
        print '~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Created Issues    : ', _comics.issues.count() - issue_count
        print 'Created Titles    : ', _comics.titles.count() - title_count
        print 'Created Publishers: ', _comics.publishers.count() - publisher_count
        print '~~~~~~~~~~~~~~~~~~~~~~~~'
        return data
    return wrapper


class DailyDownloadImporter(BaseImporter):
    """
    Imports the daily download from TFAW
    """
    def __init__(self, days, affiliate_id, supported_publishers, *args, **kwargs):
        super(DailyDownloadImporter, self).__init__(*args, **kwargs)
        self.days = days
        self.affiliate_id = affiliate_id
        self.supported_publishers = supported_publishers

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
        r = requests.get(base_url, params=payload)
        return r.content

    def load(self, content):
        fieldnames = [x[2] for x in self.csv_rules]
        with GzipFile(fileobj=StringIO(content)) as f:
            reader = DictReader(f, fieldnames=fieldnames, delimiter=self.delimiter)
            data = [row for row in reader]
        return data

    @daily_download_report
    def process(self, raw_data):
        csv_rules = {x[2]: x[3] for x in self.csv_rules}
        data = []
        for row in raw_data:
            record = self.record(self.affiliate_id, self.supported_publishers, self.days, row, csv_rules)
            if record.is_relevent():
                issue = record.run()
                # data.append(issue)
                data.append(record)
        return data


class WeeklyReleasesImporter(BaseImporter):
    """
    Processes releases
    """
    def __init__(self, week, affiliate_id, supported_publishers, *args, **kwargs):
        super(WeeklyReleasesImporter, self).__init__(*args, **kwargs)
        self.week = week
        self.date = self.week_handler(week)
        self.affiliate_id = affiliate_id
        self.supported_publishers = supported_publishers

    def download(self, *args, **kwargs):
        """
        Gets file containing a list of shippments from Diamond Distributers.
        This file is served from TFAW's servers. Three files are available at 
        any given time; thisweek, nextweek, twoweeks. They describe shipments 
        pertaining to their respective timeframes.

        :param week: String designating which diamond list to download 
                     Options: 'thisweek', 'nextweek', 'twoweeks'
        """
        if self.week not in ['thisweek', 'nextweek', 'twoweeks']:
            raise Exception('Not a valid input for week selection')
        base_url = 'http://www.tfaw.com/intranet/diamondlists_raw.php'
        payload = {
            'mode': self.week,
            'uid': self.affiliate_id,
            'show%5B%5D': 'Comics',
            'display': 'text_raw'
        }
        r = requests.get(base_url, params=payload)

        return r.content

    def load(self, content):
        """
        Turns returned content from a request for a Diamond list into someting
        we can work with. It discards any items that do not have a vender matching
        a vender in 'SUPPORTED_DIAMOND_PUBS' settings variable. It also discards any
        item whose discount code is not a D or and E.

        :param raw_content: html content returned from TFAWs servers, diamond list
        """
        html = BeautifulSoup(content)
        f = StringIO(html.pre.string.strip(' \t\n\r'))
        fieldnames = [x[2] for x in self.csv_rules]
        incsv = DictReader(f, fieldnames=fieldnames)
        return [x for x in incsv]

    def process(self, raw_content_dict):
        data = []
        csv_rules = {x[2]: x[3] for x in self.csv_rules}
        already_scheduled = _comics.issues.find_issue_with_date(self.date)
        for issue in already_scheduled:
            issue.on_sale_date = None
            _comics.issues.save(issue)
        for row in raw_content_dict:
            record = self.record(self.date, self.supported_publishers, row, csv_rules)
            if record.is_relevent():
                result = record.run()
                data.append(result)
        return data

    def week_handler(self, week):
        if week not in ['thisweek', 'nextweek', 'twoweeks']:
            raise Exception('Not a valid input for week selection')
        if week == 'thisweek':
            date = current_wednesday()
        if week == 'nextweek':
            date = next_wednesday()
        if week == 'twoweeks':
            date = two_wednesdays()
            # raise NotImplementedError
        return date

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
            if tag in x[0] and x[0] not in ['pre_process', 'post_process', 'get_processors', 'process']]
        return processors

    def pre_process(self):
        temp = deepcopy(self.raw_record)
        temp = {key: temp[key] for key in temp.keys() if self.csv_rules[key]}
        for method in self.pre_processes:
            result = getattr(self, method)(temp)
            temp.update(result)
        return temp

    def post_process(self):
        results = {}
        for method in self.post_processes:
            result = getattr(self, method)(self.object)
            results[method] = result
        return results

    def process(self):
        raise NotImplementedError

    def run(self):
        try:
            record = self.pre_process()
            self.object = self.process(record)
            if self.object:
                results = self.post_process()
        except:
            pass
        return self.object

    def is_relevent(self):
        return True


class WeeklyReleaseRecord(BaseRecord):
    def __init__(self, date, supported_publishers, *args, **kwargs):
        super(WeeklyReleaseRecord, self).__init__(*args, **kwargs)
        self.supported_publishers = supported_publishers
        self.date = date

    def is_relevent(self):
        """
        Strips the publisher string of an asterisk (*) and chesk to see if it is a
        publisher in the supported publishers attribute. Also limits relevency to
        issues with a D or an E in the discount code slot.
        """
        try:
            if self.raw_record['publisher'].strip('*') in self.supported_publishers:
                if self.raw_record['discount_code'] in ['D', 'E']:
                    return True
            return False
        except:
            return False

    def process(self, record):
        """
        Gets an issue object from the database, returns None if issue with
        given diamond id is not present.
        """
        issue = _comics.issues.first(diamond_id=record['diamond_id'])
        return issue

    def pre_massage_diamond_id(self, record, key='diamond_id'):
        """
        Removes a trailing letter (A-Z) from a diamond id if its present
        """
        if record[key][-1:].isalpha():
            diamond_id = record[key][:-1]
        else:
            diamond_id = record[key]
        return {key: diamond_id}

    def post_set_release_date(self, issue):
        """
        Sets release data of issue object to the class's date attribute
        """
        issue.on_sale_date = self.date
        _comics.issues.save(issue)
        return True

class DailyDownloadRecord(BaseRecord):
    """
    Represents a single record in the daily download
    """
    def __init__(self, affiliate_id, supported_publishers, look_ahead=10, *args, **kwargs):
        super(DailyDownloadRecord, self).__init__(*args, **kwargs)
        self.affiliate_id = affiliate_id
        self.supported_publishers = supported_publishers
        self.look_ahead = look_ahead

    def is_relevent(self):
        if self.raw_record['category'] == 'Comics':
            if self.raw_record['publisher'] in self.supported_publishers:
                release_date = self.pre_current_tfaw_release_date(self.raw_record)
                if release_date['current_tfaw_release_date'] > (datetime.now().date() - timedelta(days=7)) \
                    and release_date['current_tfaw_release_date'] < (datetime.now().date() + timedelta(days=self.look_ahead)):
                    return True
        return False

    def process(self, record):
        """
        Inserts an issue into the database. This requires creating / getting
        both a publisher object and a title object first.
        """
        if not record:
            raise Exception
        issue_dict = deepcopy(record)
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
        return issue

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
        """
        Converts the retail price string into a float object
        """
        result = float(record[key]) if self.is_float(record[key]) else None
        return {key: result}

    def pre_a_link(self, record, key='a_link'):
        """
        Replaces YOURUSERID with the SAS affiliate id
        """
        result = record[key].replace('YOURUSERID', self.affiliate_id)
        return {key: result}

    def pre_diamond_id(self, record, key='diamond_id'):
        """
        Splits a diamond id into two objects: base diamond id and discount code
        """
        if record[key][-1:].isalpha():
            diamond_id = record[key][:-1]
            discount_code = record[key][-1:]
        else:
            diamond_id = record[key]
            discount_code = None
        return {key: diamond_id, 'discount_code': discount_code}

    def pre_description(self, record, key='description'):
        """
        Converts HTML entities in the description field

        http://stackoverflow.com/questions/18220631/encoding-a-string-with-ascii-characters-find-and-replace
        """
        result = HTMLParser().unescape(record[key])
        return {key: result}

    def pre_current_tfaw_release_date(self, record, key='current_tfaw_release_date'):
        """
        Converts the text representation of the release date attribute to a
        datetime object.
        """
        result = datetime.strptime(record[key], '%Y-%m-%d').date()
        return {key: result}

    def pre_last_updated(self, record, key='last_updated'):
        """
        Converts the text representaiton of the last_updated attribute to a 
        datetime object.
        """
        result = datetime.strptime(record[key], '%Y-%m-%d %H:%M:%S')
        return {key: result}

    def post_parent_status(self, issue):
        """
        Checks to see if the imported issue is the parent issue in a grouping
        of issues. This is how we determine which issue to display when it 
        has alternative covers.
        """
        similar_issues = _comics.issues.filter(
            _comics.issues.__model__.title == issue.title,
            _comics.issues.__model__.issue_number == issue.issue_number,
            _comics.issues.__model__.diamond_id != issue.diamond_id
        )
        match = re.search(r'\d+', issue.diamond_id)
        current_issue_number = int(match.group())
        is_parent = True
        for i in similar_issues:
            match = re.search(r'\d+', i.diamond_id)
            if int(match.group()) < current_issue_number:
                is_parent = False
        if is_parent:
            issue.is_parent = True
            if similar_issues:
                issue.has_alternates = True
                for i in similar_issues:
                    i.is_parent = False
                    i.has_alternates = True
                    _comics.issues.save(i)
            _comics.issues.save(issue)
        return is_parent

    def post_cover_image(self, issue):
        """
        Downloads and processes the cover image of the issue object.
        """
        created = _comics.issues.set_cover_image_from_url(issue, issue.big_image)
        return created

if __name__ == "__main__":
    print 'WHOOPS!'
