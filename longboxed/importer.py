import gzip

from csv import DictReader


class BaseImporter(object):
    """
    Base csv importer class
    """
    def __init__(self, delimiter='|', filename='/path/to/csv/file.txt'):
        self.filename = filename
        self.raw_data = []
        self.processed_data = []
        self.csv_rules = None
        self.delimiter = delimiter

    def load(self, filename):
        fieldnames = [x[2] for x in self.csv_rules]
        with gzip.open(ffile, 'rb') as f:
            reader = DictReader(f, fieldnames=fieldnames, delimiter=self.delimiter)
            self.raw_data = [row for row in reader]
        return self.raw_data

class DailyDownloadImporter(BaseImporter):
    """
    Imports the daily download from TFAW
    """
    pass

class DailyDownloadRecord(object):
    """
    Represents a single record in the daily download
    """
    def __init__(self):
        pass