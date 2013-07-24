from flask import Flask, render_template
# from flask.ext.mongokit import MongoKit
# from flask.ext.mongoengine import MongoEngine
from mongoengine import *
from flask.ext.mongoengine import MongoEngine
import datetime

app = Flask(__name__)
app.config.from_object('longboxed.settings')

db = MongoEngine()
db.init_app(app)
db.connect('thisweekscomics')

class ComicInfo(EmbeddedDocument):
    name = StringField()
    issue_number = FloatField()
    issues = FloatField()
    other = StringField()
    complete_title = StringField()
    one_shot = BooleanField()


class Comic(Document):
    meta = {'collection': 'comics'}
    productID = StringField()
    info = EmbeddedDocumentField(ComicInfo)
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
    id = StringField()
    category = StringField()
    upc = StringField()


@app.route('/')
def index():
    comics = Comic.objects.all()
    for comic in comics:
        print comic.info.name
    return 'comics'


# class Todo(db.Document):
#     title = db.StringField(max_length=60)
#     text = db.StringField()
#     done = db.BooleanField(default=False)
#     pub_date = db.DateTimeField(default=datetime.datetime.now)


# @app.route('/')
# def index():
#     # As a list to test debug toolbar
#     Todo.objects().delete()  # Removes
#     Todo(title="Simple todo A ", text="12345678910").save()  # Insert
#     Todo(title="Simple todo B", text="12345678910").save()  # Insert
#     Todo.objects(title__contains="B").update(set__text="Hello world")  # Update
#     todos = list(Todo.objects[:10])
#     todos = Todo.objects.all()
#     return render_template('index.html', todos=todos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)