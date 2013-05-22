from previewsScraper import getComics
from mongokit import Connection, Document
import sys

from models import Comic

MONGO_USERNAME = 'bueno'
MONGO_PASSWORD = 'Cry9Gas'
MONGO_DBNAME = 'thisweekscomics'
MONGO_HOST = 'ds031877.mongolab.com'
MONGO_PORT = 31877
MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (MONGO_USERNAME, MONGO_PASSWORD,
                                          MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

mongo = Connection(MONGO_URI)
mongo.register([Comic])
collection = mongo[MONGO_DBNAME]

def store_comic(comic):
    try:
        if collection.comics.Comic.find_one({"id": comic['id']}):
            c = collection.comics.Comic.find_one({"id": comic['id']})
        else:
            c = collection.comics.Comic()
        c.id = comic['id']
        c.title = comic['title']
        c.publisher = comic['publisher']
        c.price = comic['price']
        c.link = comic['link']
        c.date = comic['date']
        c.image_url = comic['image_url']
        c.save()
    except:
        print "Unexpected error:", sys.exc_info()[1]

if __name__ == "__main__":
    # url = "http://www.previewsworld.com/Home/1/1/71/952" # New Releases
    url = "http://www.previewsworld.com/Home/1/1/71/954" # Upcoming Releases

    comicDict = getComics(url)

    for key in comicDict.keys():
        for comic in comicDict[key]:
            store_comic(comic)