# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""

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

# Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console