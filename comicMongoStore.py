# TODO: put mongoURL in environment variable

from datetime import datetime
from datetime import timedelta

from previewsScraper import getComics

from pymongo import Connection

MONGO_USERNAME = 'bueno'
MONGO_PASSWORD = 'Cry9Gas'
MONGO_DBNAME = 'thisweekscomics'
MONGO_HOST = 'ds031877.mongolab.com'
MONGO_PORT = 31877
MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (MONGO_USERNAME, MONGO_PASSWORD,
                                          MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

class comicMongo(object):

    def __init__(self, mongoURL = 'mongodb://heroku:93f17e34f76c9902ad0b574509c98040@linus.mongohq.com:10002/app15098233'):
        self.connection = Connection(mongoURL)
        self.db = self.connection.app15098233
        self.collection = self.db.comicDB

    def store_comics(self ,d = 0):

        if d == 0:
            url = "http://www.previewsworld.com/Home/1/1/71/952" # New Releases
        else:
            url = "http://www.previewsworld.com/Home/1/1/71/954" # Upcoming Releases
        
        comicDict = getComics(url)

        # for key in comicDict.keys():
        #     comics = {}
        #     comics['publisher'] = key
        #     comics['date'] = comicDict[key][0]['date']
        #     comics['comics'] = comicDict[key]
        #     self.db.comicDB.insert(comics)

        for key in comicDict.keys():
            for comic in comicDict[key]:
                diamondcode = comic['id']
                self.collection.update({"id": diamondcode} ,comic, upsert=True)

        return

    def find_issue_by_id(self, diamondid=None):
        if diamondid:
            result = self.collection.find_one({"id": diamondid})
            return result
        else:
            return None


    def find_all_comics_by_date(self, date = datetime.now()):
        result = []
        for document in self.collection.find({"date": date}):
            result.append(document)

        result = sorted(result, key=lambda k: k['publisher'])

        return result

    def find_comics_in_date_range(self, start, end):
        result = []
        for document in self.collection.find({"date": {"$gte": start, "$lt": end}}):
            result.append(document)

        result = sorted(result, key=lambda k: k['publisher'])

        return result

    def get_current_week(self):

        today = datetime.today()
        day_of_week = today.weekday()
        to_beginning_of_week = timedelta(days=day_of_week)
        beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)

        to_end_of_week = timedelta(days= (6 - day_of_week))
        end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)

        return (beginning_of_week, end_of_week)

    def get_wednesday(self):

        b, e = self.get_current_week()

        wednesday = b + timedelta(days=2)

        return wednesday




if __name__ == "__main__":

    cMongo = comicMongo()
    # start, end = cMongo.get_current_week()
    # wed = cMongo.get_wednesday()
    # cMongo.store_comics(0)
    cMongo.find_issue_by_id('MAR130405')

    # print wed
    # result = cMongo.find_comics_in_date_range(start, end)
    # for r in result:
        # print r['publisher'], r['date']