#!/usr/bin/env python
# coding=utf8

from flask import (Flask, g, render_template,
                    request, flash, redirect, session,
                    url_for, jsonify, abort)
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from flask.ext.wtf import Form, BooleanField, SelectField
from mongokit import Connection, Document
from rauth.service import OAuth2Service

from datetime import datetime, timedelta
from dateutil import tz
import difflib
import requests
import sys
import json

from models import Comic
# 4
# MongoLab configuration
MONGO_USERNAME = 'bueno'
MONGO_PASSWORD = 'Cry9Gas'
MONGO_DBNAME = 'thisweekscomics'
MONGO_HOST = 'ds031877.mongolab.com'
MONGO_PORT = 31877
MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (MONGO_USERNAME, MONGO_PASSWORD,
                                          MONGO_HOST, MONGO_PORT, MONGO_DBNAME)

# Bootstrap Configuration
BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_FONTAWESOME = True

# Flask Application Configuration
SECRET_KEY = '***REMOVED***'

# Create the application object
app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'adslfkjewwa12r23f23'
app.jinja_options['extensions'].append('jinja2.ext.loopcontrols')

# Bootstrap Setup
Bootstrap(app)

# Create the Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# Create database connection
mongo = Connection(app.config['MONGO_URI'])

# Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console

# rauth OAuth 2.0 service wrapper
service = OAuth2Service(
            name='google',
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            access_token_url='https://accounts.google.com/o/oauth2/token',
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            base_url='https://www.google.com/accounts/')

# ===================================

# ===================================
# 
# User Class
#
# ===================================
def max_length(length):
    def validate(value):
        if len(value) <= length:
            return True
        raise Exception('%s must be at most %s characters long' % length)
    return validate

@mongo.register
class User(Document, UserMixin):
    structure = {
        'id': unicode,
        'info': {
            'full_name': unicode,
            'first_name': unicode,
            'last_name': unicode,
            'gender': unicode,
            'birthday': datetime,
            'email': unicode
        },
        'comics': {
            'favorites': [unicode]
        },
        'settings': {
            'display_favs': bool,
            'default_cal': unicode
        },
        'tokens': {
            'refresh_token': unicode,
            'access_token': unicode,
            'expire_time': datetime,

        },
        'date_creation': datetime
    }
    validators = {
        'info.full_name': max_length(50),
        'info.email': max_length(120)
    }
    required_fields = ['id', 'info.email', 'date_creation']
    default_values = {
        'date_creation': datetime.utcnow,
        'settings.display_favs': True
    }
    use_dot_notation = True
    def __repr__(self):
        return '<User %r>' % (self.name)

# ===================================
# 
# Comic Book Class
# (DOESNT DO ANYTHING YET)
# ===================================
# @mongo.register
# class Comic(Document, UserMixin):
#     structure = {
#         'id': unicode,
#         'publisher': unicode,
#         'title': unicode,
#         'price': float,
#         'link': unicode,
#         'date_released': datetime,
#         'last_updated': datetime
#     }
#     required_fields = ['id', 'title']
#     default_values = {
#         'last_updated': datetime.utcnow
#     }
#     use_dot_notation = True
#     def __repr__(self):
#         return '<Comic %r>' % (self.name)

mongo.register([Comic])
collection = mongo[MONGO_DBNAME]

# ===================================
# 
# Application Routes
#
# ===================================

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def site_error(e):
    return render_template('404.html'), 500

@app.route("/")
def index():
    # day = get_wednesday()
    start, end = get_current_week()
    dates = {}
    dates['start'] = start
    dates['end'] = end
    comicList = find_comics_in_date_range(start, end)

    # print 'START ', start
    # print 'END ', end
    # print 'COMICLIST: ', comicList

    matches = []
    if g.user is not None:
        if g.user.comics.favorites:
            matches = get_favorite_matches(g.user.comics.favorites, comicList)
    # print "MATCHES: ", matches
    return render_template('main.html', comicList=comicList, dates=dates, matches=matches) 

@app.route('/comics', methods=['GET','POST'])
def comics():
    start, end = get_current_week()
    dates = {}
    dates['today'] = end.strftime('%B %-d, %Y')
    dates['lastweek'] = start.strftime('%B %-d, %Y')
    dates['start'] = start
    dates['end'] = end
    # day = cMongo.get_wednesday()
    comicList = find_comics_in_date_range(start, end)

    matches = []
    if g.user is not None:
        if g.user.comics.favorites:
            matches = get_favorite_matches(g.user.comics.favorites, comicList)
    return render_template('comics.html', dates=dates, comicList=comicList, calendarenable=1, matches=matches)

@app.route('/favorites', methods=['GET','POST'])
@login_required
def favorites(): 
    if g.user is not None:
        if request.method == 'POST':
            try:
                g.user.comics.favorites.append(request.form['newfavorite'])
                g.user.comics.favorites.sort()
                g.user.save()
            except:
                pass
    else:
        return redirect(url_for('index'))
    return render_template('favorite_comics.html', g=g)

# Individual issue page
@app.route('/issue/<diamondid>')
def issue(diamondid):
    # try:
    # print 'DIAMONDID ', diamondid
    issue = collection.comics.find_one({"id": diamondid})
    # print 'ISSUE ', issue
    if issue:
        return render_template('issue.html', issue=issue)
    return abort(404) 
    # except:
    #     print "Unexpected error:", sys.exc_info()[1]
    #     return abort(404) 

@app.route('/remove_favorite', methods=['POST'])
@login_required
def remove_favorite(): 
    if g.user is not None:
        if request.method == 'POST':
            try:
                # Get the index of the book to delete
                i = int(request.form['comic_to_remove'])
                # Delete comic at desired index
                del g.user.comics.favorites[i]
                # Save updated user
                g.user.save()
            except:
                print "Unexpected error:", sys.exc_info()[1]
    else:
        return redirect(url_for('index'))
    return redirect(url_for('favorites'))

@app.route('/settings', methods=['GET','POST'])
@login_required
def settings():
    if current_user is not None:
        if request.method == 'POST':
            try:
                if 'display_favs' in request.values:
                    current_user.settings.display_favs = True
                else:
                    current_user.settings.display_favs = False
                current_user.settings.default_cal = request.form['cals']
                current_user.save()
            except:
                print "Unexpected error:", sys.exc_info()[0]
    else:
        return redirect(url_for('index'))

    # Default calendars
    calendars = get_calendar_info() # Get a users calendar
    c = []
    for cal in calendars[1]:
        c.append((cal[0], cal[1]))
    # Set the default calendar
    default_cal = current_user.settings.default_cal

    class ExampleForm(Form):
        display_favs = BooleanField(
                            'Display Favorites',
                            description=u'If a comic on your favorites list matches an issue out that week, display it inline with the other books.', 
                            default = current_user.settings.display_favs)
        cals = SelectField(
                    u'Calendars',
                    description=u'Set the calendar the you want to add comics to.',
                    choices=c,
                    default=default_cal)

    form = ExampleForm()

    return render_template('settings.html',form=form)

@app.route('/edit_profile', methods=['GET','POST'])
@login_required
def edit_profile():
    if g.user is not None:
        if request.method == 'POST':
            try:
                g.user.fullname = request.form['fullname']
                g.user.email = request.form['email']
                g.user.username = request.form['username']
                g.user.save()
            except:
                pass
    else:
        return redirect(url_for('index'))

    return render_template('edit_profile.html')

@app.route('/add_issue_to_cal')
@login_required
def add_issue_to_cal():
    try:
        diamondid = request.args.get('id')
        issue = collection.comics.Comic.find_one({'id': diamondid})
        if issue:
            event = {
                'summary': issue.info.complete_title,
                'start': {
                    'date': issue.onSaleDate.strftime('%Y-%m-%d')
                },
                'end': {
                    'date': issue.onSaleDate.strftime('%Y-%m-%d')
                }
            }
            response = insert_calendar_event(event)
            if response:
                return jsonify(response=200, title=str(issue.info.complete_title))
            else:
                return jsonify(response=201)
        return jsonify(response=500)
    except:
        print "Unexpected error [/add_issue_to_cal]:", sys.exc_info()[1]
        return jsonify(response=500)


# ===================================
# 
# Google Calendar Methods
#
# ===================================

# Need to make this a little better
def current_headers():
    headers = {'Authorization': 'Bearer '+current_user.tokens.access_token,
                'X-JavaScript-User-Agent':  'Google       APIs Explorer',
                'Content-Type':  'application/json'}
    return headers

# def insert_calendar_event(event):
#     headers = current_headers()
#     endpoint = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % current_user.settings.default_cal
#     response = requests.post(endpoint, headers=headers, data=json.dumps(event))
#     return

def insert_calendar_event(new_event):
    headers = current_headers()
    endpoint = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % current_user.settings.default_cal
    
    # Check all events on given day
    day = datetime.strptime(new_event['start']['date'], '%Y-%m-%d')
    events = events_on_day(current_user.settings.default_cal, day)
    
    # Check if event has already been added based on summaries
    insert_event = True
    if events:
        for event in events:
            if event['summary'] == new_event['summary']:
                insert_event = False
                break
    if insert_event:
        response = requests.post(endpoint, headers=headers, data=json.dumps(new_event))
        return True
    return False

def events_on_day(cal, day):
    headers = current_headers()
    endpoint = endpoint = 'https://www.googleapis.com/calendar/v3/calendars/%s/events' % cal
    
    start = datetime(day.year, day.month, day.day, tzinfo=tz.tzutc())
    end = start + timedelta(1)
    data = {
        'timeMin': start.isoformat(),
        'timeMax': end.isoformat()
    }
    response = requests.get(endpoint, headers=headers, params=data)
    r = response.json()
    if 'items' in r:
        print 'FOUND EVENTS!!!!'
        return r['items']

    print 'NO EVENTS FOUND'
    return None

def get_calendar_info():
    headers = {'Authorization': 'Bearer '+current_user.tokens.access_token}
    data = {'minAccessRole':'owner'}
    endpoint = 'https://www.googleapis.com/calendar/v3/users/me/calendarList'
    response = requests.get(endpoint, headers=headers, params=data)
    r = response.json()

    calendars = []
    default_cal = None
    for cal in r['items']:
        name = cal['summary']
        calid = cal['id']
        try:
            if cal['primary']:
                default_cal = (cal['id'], cal['summary'], True)
                primary = True
        except KeyError:
            primary = False

        calendars.append((calid, name, primary))

    return (default_cal, calendars)

# ===================================
# 
# AJAX helper routes
#
# ===================================
@app.route('/get_comicpage', methods=['POST'])
def get_favorites():
    start = datetime.strptime(request.form['start'], '%B %d, %Y')
    end = datetime.strptime(request.form['end'], '%B %d, %Y')

    comicList = find_comics_in_date_range(start, end)

    try:
        nav = render_template('comicsidenav.html', comicList=comicList)
    except:
        nav = None
    try:
        clist = render_template('comiclist.html', comicList=comicList)
    except:
        clist = None
    try:
        matches = None
        if g.user is not None:
            if g.user.comics.favorites:
                matches = []
                matches = get_favorite_matches(g.user.comics.favorites, comicList)
                if matches:
                    matches = render_template('favorite_matches.html', matches=matches)
    except:
        matches = None

    # return the html as json for jquery to insert
    return jsonify(nav=nav, clist=clist, matches=matches)


# ===================================
# 
# User Session Management
#
# ===================================
@login_manager.user_loader
def load_user(userid):
    return get_user_with_google_id(userid)

@app.before_request
def before_request():
    if not current_user.is_anonymous():
        if datetime.utcnow() > current_user.tokens.expire_time:
            # print "GETTING NEW TOKEN!!"
            auth_response = service.get_raw_access_token(data={
                'refresh_token': current_user.tokens.refresh_token,
                'grant_type': 'refresh_token'
            })
            auth_data = auth_response.json()

            current_user.tokens.access_token = auth_data['access_token']
            current_user.tokens.expire_time = datetime.utcnow() + timedelta(seconds=int(auth_data['expires_in']))
            current_user.save()

        g.user = current_user

    else:
        g.user = None

@app.route('/logout')
@login_required
def logout():
    logout_user()
    g.user = None
    return redirect(url_for('index'))

# ===================================
# 
# Google OAuth Routes
#
# ===================================
@app.route('/login', methods=['GET','POST'])
def login():
    if current_user is not None and current_user.is_authenticated():
        return redirect(url_for('index'))
    params={'scope': 'openid email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar',
            'response_type': 'code',
            'access_type': 'offline',
            'redirect_uri': url_for('authorized', _external=True)}
    return redirect(service.get_authorize_url(**params))

@app.route(REDIRECT_URI)
def authorized():
    if not 'code' in request.args:
        flash('DID NOT AUTHORIZE')
        return redirect(url_for('index'))

    # make a request for the access token credentials using code
    redirect_uri = url_for('authorized', _external=True)
    data = dict(code=request.args['code'], grant_type='authorization_code', redirect_uri=redirect_uri)

    auth_response = service.get_raw_access_token(data=data)
    auth_data = auth_response.json()

    # Get the user identity
    headers = {'Authorization': 'OAuth '+auth_data['access_token']}
    identity_response = requests.get('https://www.googleapis.com/oauth2/v1/userinfo',
                                     headers=headers)
    identity_data = identity_response.json()

    if not get_user_with_google_id(identity_data['id']):
        # print "CREATING NEW USER"
        identity = identity_data
        identity['access_token'] = auth_data['access_token']
        print 'AUTH_DATA ', auth_data
        identity['refresh_token'] = auth_data['refresh_token']
        create_new_user(identity)

    # Get the user and save token
    u = get_user_with_google_id(identity_data['id'])
    u.tokens.access_token = auth_data['access_token']
    u.tokens.expire_time = datetime.utcnow() + timedelta(seconds=int(auth_data['expires_in']))
    u.save()

    # Login the user
    login_user(u)
    g.user = current_user

    return redirect(url_for('index'))

# ===================================
# 
#  User Database Functions
#
# ===================================
def create_new_user(resp):
    # Create new user
    newUser = collection.users.User()
    newUser.id = resp['id']
    # User Info
    newUser.info.email = resp['email']
    newUser.info.first_name = resp['given_name']
    newUser.info.last_name = resp['family_name']
    newUser.info.full_name = resp['name']
    # Set default calendar
    newUser.settings.default_cal = resp['email']

    # Save tokens
    newUser.tokens.access_token = resp['access_token']
    newUser.tokens.refresh_token = resp['refresh_token']
    newUser.save()
    return

def get_user_with_google_id(gid):
    user_data = collection.users.User.find_one({"id": gid})
    return user_data

# ===================================
# 
#  Comic Specific Functions
#
# ===================================
def find_all_comics_by_publisher(publisher):
    result = list(collection.comics.Comic.find({"publisher": publisher}))
    return result

def find_all_comics_by_date(date = datetime.now()):
    result = list(collection.comics.Comic.find({"date": date}))
    result = sorted(result, key=lambda k: k.publisher)
    return result

def find_comics_in_date_range(start, end):
    result = list(collection.comics.Comic.find({"onSaleDate": {"$gte": start, "$lt": end}}))
    result = sorted(result, key=lambda k: k.publisher)
    return result

def get_current_week():
    today = datetime.today()
    day_of_week = today.weekday()
    to_beginning_of_week = timedelta(days=day_of_week)
    beginning_of_week = (today - to_beginning_of_week).replace(hour=0, minute=0, second=0, microsecond=0)
    to_end_of_week = timedelta(days= (6 - day_of_week))
    end_of_week = (today + to_end_of_week).replace(hour=0, minute=0, second=0, microsecond=0)

    return (beginning_of_week, end_of_week)

def get_wednesday():
    b, e = get_current_week()
    wednesday = b + timedelta(days=2)
    return wednesday

def get_favorite_matches(favorites, comicList):
    matches = []
    if g.user.settings.display_favs:
        for idx, comic in enumerate(favorites):
            print idx, comic
            # for c in comicList:
            #     if c.info.name == None:
            #         print c.info
            match = difflib.get_close_matches(comic, [c.info.name for c in comicList if c.info])
            print "Match: ", match
            matches = matches + match

    matchingComics = [dictio for dictio in comicList if dictio.info.name in matches]
    return matchingComics


# ===================================
# 
# Run the Application
#
# ===================================
if __name__ == "__main__":
    app.run(debug=True)
    # new_user()

