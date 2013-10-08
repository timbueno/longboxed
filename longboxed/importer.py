import gzip
import inspect

from csv import DictReader

import requests

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
    def __init__(self, raw_record, process_func_tag='process'):
        self.process_func_tag = process_func_tag
        self.processes = self.get_processors(self.process_func_tag)
        self.raw_record = raw_record
        self.processed_record = None

    def get_processors(self, tag):
        processors = [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod) \
            if tag in x[0] and x[0] != 'get_processors' and x[0] != 'process']
        return processors

    def process(self):
        self.processed_record = self.raw_record
        for method in self.processes:
            result = getattr(self, method)(self.processed_record)
            self.processed_record.update(result)
        return


class DailyDownloadRecord(BaseRecord):
    """
    Represents a single record in the daily download
    """
    def __init__(self, affiliate_id, *args, **kwargs):
        super(DailyDownloadRecord, self).__init__(*args, **kwargs)
        self.affiliate_id = affiliate_id

    def is_float(self, number):
        try: 
            float(number)
            return True
        except (ValueError, TypeError):
            return False

    def process_retail_price(self, record, key='retail_price'):
        result = float(record[key]) if self.is_float(record[key]) else None
        return {key: result}

    def process_a_link(self, record, key='a_link'):
        result = record[key].replace('YOURUSERID', self.affiliate_id)
        return {key: result}

    def process_diamond_id(self, record, key='diamond_id'):
        if record[key][-1:].isalpha():
            diamond_id = record[key][:-1]
            discount_code = record[key][-1:]
        else:
            diamond_id = record[key]
            discount_code = None
        return {key: diamond_id, 'discount_code': discount_code}


if __name__ == "__main__":
    csv_rules = [
        (0, 'ProductID', 'product_id', True),
        (1, 'Name', 'complete_title', True),
        (2, 'MerchantID', 'merchant_id', False),
        (3, 'Merchant', 'merchant', False),
        (4, 'Link', 'link', True),
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
        'category': 'Graphic Novels',
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

    my_record = DailyDownloadRecord(record)
    # my_record.process()
    print type(my_record.raw_record['retail_price'])
    my_record.process()
    print type(my_record.processed_record['retail_price'])
    # my_importer = DailyDownloadImporter('782419', my_record)
    # print my_importer.csv_rules
    # print my_importer.record
