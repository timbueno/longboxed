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

# Flask-Security Configuration
SECURITY_REGISTERABLE = True
# # SECURITY_SEND_REGISTER_EMAIL = False
# SECURITY_LOGIN_WITHOUT_CONFIRMATION = True
# SECURITY_EMAIL_SENDER = 'postmaster@longboxed.mailgun.org'
SECURITY_POST_LOGIN_URL = '/'
SECURITY_PASSWORD_HASH = 'plaintext'
SECURITY_PASSWORD_SALT = 'password_salt'
SECURITY_REMEMBER_SALT = 'remember_salt'
SECURITY_RESET_SALT = 'reset_salt'
SECURITY_RESET_WITHIN = '5 days'
SECURITY_CONFIRM_WITHIN = '5 days'
SECURITY_SEND_REGISTER_EMAIL = False

# Mail configuration
MAIL_SERVER = 'smtp.mailgun.org'
MAIL_PORT = 587
MAIL_USERNAME = 'postmaster@longboxed.mailgun.org'
MAIL_PASSWORD = '0xcp43by5fb6'

# Bootstrap Configuration
BOOTSTRAP_USE_MINIFIED = True
BOOTSTRAP_FONTAWESOME = True

# # Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console