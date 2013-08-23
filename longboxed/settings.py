# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""
from datetime import timedelta

DEBUG = True

# Flask Application Configuration
SECRET_KEY = '***REMOVED***'

# URIS
SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/longboxed'

# Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERYBEAT_SCHEDULE = {
    'test-every-30-seconds': {
        'task': 'tasks.test',
        'schedule': timedelta(seconds=600)
    },
}
CELERY_TIMEZONE = 'UTC'

# Bootstrap Configuration
BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_FONTAWESOME = True

# # Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console