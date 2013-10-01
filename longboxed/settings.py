# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""
from datetime import timedelta

DEBUG = True

# Longboxed Specific Variables
AFFILIATE_ID = '782419'
SUPPORTED_PUBS = ['Marvel Comics', 'DC Comics', 'Dark Horse', 'IDW Publishing',\
                  'Boom! Studios', 'Image Comics', 'Dynamite Entertainment', \
                  'Avatar Press', 'Abstract Studios','Archie Comics', \
                  'Vertigo', 'Valiant Comics']

SUPPORTED_DIAMOND_PUBS = ['MARVEL COMICS', 'DC COMICS', 'DARK HORSE COMICS', \
                          'IDEA & DESIGN WORKS LLC', 'BOOM ENTERTAINMENT', 'IMAGE COMICS',\
                          'DYNAMIC FORCES','ABSTRACT STUDIOS', 'AVATAR PRESS INC', \
                          'ARCHIE COMIC PUBLICATIONS', 'VALIANT ENTERTAINMENT LLC']

# Flask Application Configuration
SECRET_KEY = '***REMOVED***'

# URIS
SQLALCHEMY_DATABASE_URI = 'postgres://app_user:password@localhost/longboxed'

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERYBEAT_SCHEDULE = {
    'test-every-30-seconds': {
        'task': 'tasks.test',
        'schedule': timedelta(seconds=600)
    },
}
CELERY_TIMEZONE = 'UTC'

# Flask-Security Configuration
SECURITY_REGISTERABLE = True
SECURITY_SEND_REGISTER_EMAIL = True
SECURITY_CONFIRMABLE = True
SECURITY_LOGIN_WITHOUT_CONFIRMATION = True

# SECURITY_POST_CONFIRM_VIEW = '/set_something_up'

SECURITY_TRACKABLE = True
SECURITY_POST_LOGIN_URL = '/'

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT= '***REMOVED***'
SECURITY_REMEMBER_SALT = '***REMOVED***'
SECURITY_RESET_SALT = '***REMOVED***'
SECURITY_CHANGABLE = True
SECURITY_RESET_WITHIN = '5 days'
SECURITY_CONFIRM_WITHIN = '5 days'

SECURITY_EMAIL_SENDER = 'no-reply@longboxed.com'
SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome to Longboxed!'
SECURITY_EMAIL_SUBJECT_CONFIRM = 'Please confirm your Longboxed email!'

# Mail configuration
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USERNAME = 'postmaster@longboxed.com'
MAIL_PASSWORD = '***REMOVED***'

# Bootstrap Configuration
BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_FONTAWESOME = True
BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT = 'UA-44481415-1'

# # Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console