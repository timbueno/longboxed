# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""
DEBUG = True

# Flask Application Configuration
SECRET_KEY = '***REMOVED***'

SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1:3306/longboxed'


# MONGODB_SETTINGS = {
#     'alias': 'default',
#     'USERNAME': 'bueno',
#     'PASSWORD': 'Cry9Gas',
#     'DB': 'thisweekscomics',
#     'HOST': 'ds031877.mongolab.com',
#     'PORT': 31877
# }

# Bootstrap Configuration
BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_FONTAWESOME = True

# # Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console