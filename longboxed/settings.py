# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""
from datetime import timedelta
from os import environ

DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False

USE_AWS = True
AWS_S3_BUCKET = 'longboxed'
AWS_ACCESS_KEY_ID = '***REMOVED***'
AWS_SECRET_KEY = '***REMOVED***'

THUMBNAIL_WIDTHS = [100, 250, 500]

# Longboxed Specific Variables
AFFILIATE_ID = '782419'
SUPPORTED_PUBS = ['Marvel Comics', 'DC Comics', 'Dark Horse', 'IDW Publishing',\
                  'Boom! Studios', 'Image Comics', 'Dynamite Entertainment', \
                  'Avatar Press', 'Abstract Studios','Archie Comics', \
                  'Vertigo', 'Valiant Comics']

SUPPORTED_DIAMOND_PUBS = ['MARVEL COMICS', 'DC COMICS', 'DARK HORSE COMICS', \
                          'IDEA & DESIGN WORKS LLC', 'BOOM ENTERTAINMENT', 'IMAGE COMICS',\
                          'DYNAMIC FORCES','ABSTRACT STUDIOS', 'AVATAR PRESS INC', \
                          'ARCHIE COMIC PUBLICATIONS', 'VALIANT ENTERTAINMENT LLC', \
                          'IDW PUBLISHING']

# Flask Application Configuration
SECRET_KEY = '***REMOVED***'

# URIS
# SQLALCHEMY_DATABASE_URI = 'postgres://app_user:password@localhost/longboxed'
SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']

CSV_RULES = [
    (0, 'ProductID', 'product_id', True),
    (1, 'Name', 'complete_title', True),
    (2, 'MerchantID', 'merchant_id', False),
    (3, 'Merchant', 'merchant', False),
    (4, 'Link', 'a_link', True),
    (5, 'Thumbnail', 'thumbnail', True),
    (6, 'BigImage', 'big_image', True),
    (7, 'Price', 'price', False),
    (8, 'RetailPrice', 'retail_price', True),
    (9, 'Category', 'sas_category', False),
    (10, 'SubCategory', 'sas_subcategory', False),
    (11, 'Description', 'description', True),
    (12, 'OnSaleDate', 'prospective_release_date', True),
    (13, 'Genre', 'genre', True),
    (14, 'People', 'people', True),
    (15, 'Theme', 'theme', False),
    (16, 'Popularity', 'popularity', True),
    (17, 'LastUpdated', 'last_updated', True),
    (18, 'status', 'status', False),
    (19, 'manufacturer', 'publisher', True),
    (20, 'partnumber', 'diamond_id', True),
    (21, 'merchantCategory', 'category', True),
    (22, 'merchantSubcategory', 'merchant_subcategory', False),
    (23, 'shortDescription', 'short_description', False),
    (24, 'ISBN', 'isbn', False),
    (25, 'UPC', 'upc', True)
]

RELEASE_CSV_RULES = [
    (0, 'ITEMCODE', 'diamond_id', True),
    (1, 'DiscountCode', 'discount_code', True),
    (2, 'TITLE', 'complete_title', True),
    (3, 'PRICE', 'retail_price', True),
    (4, 'Vendor', 'publisher', True)
]

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

SOCIAL_GOOGLE = {
    'consumer_key': '200273015685.apps.googleusercontent.com',
    'consumer_secret': '***REMOVED***',
    'request_token_params': {
        'scope': 'openid email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar'
    }
}

SOCIAL_FACEBOOK = {
    'consumer_key': '***REMOVED***',
    'consumer_secret': '***REMOVED***'
}

SOCIAL_TWITTER = {
    'consumer_key': '***REMOVED***',
    'consumer_secret': '***REMOVED***',
}

# # Google OAuth Setup
GOOGLE_CLIENT_ID = '200273015685.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = '***REMOVED***'
REDIRECT_URI = '/oauth2callback'  # one of the Redirect URIs from Google APIs console