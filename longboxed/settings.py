# -*- coding: utf-8 -*-
"""
    longboxed.settings
    ~~~~~~~~~~~~~~~

    longboxed settings module
"""
from datetime import timedelta
from os import environ

from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore
from sqlalchemy_imageattach.stores.s3 import S3Store


class Config(object):
    CONFIG_NAME = 'base'
    USE_AWS = False
    AWS_S3_BUCKET = environ['AWS_S3_BUCKET']
    AWS_ACCESS_KEY_ID = environ['AWS_ACCESS_KEY_ID']
    AWS_SECRET_KEY = environ['AWS_SECRET_KEY']

    CACHE_CONFIG = {'CACHE_TYPE': 'simple'}

    THUMBNAIL_WIDTHS = [100, 250, 500]

    # Longboxed Specific Variables
    AFFILIATE_ID = environ['AFFILIATE_ID']
    COMPARISON_IMAGE = 'media/tfaw_nocover.jpg'
    COMPARISON_IMAGE_URL = 'http://affimg.tfaw.com/covers_tfaw/400/no/nocover.jpg'
    DISABLED_PUBS = ['Dark Horse']
    SUPPORTED_PUBS = ['Marvel Comics', 'DC Comics', 'Dark Horse',
                      'IDW Publishing', 'Boom! Studios', 'Image Comics',
                      'Dynamite Entertainment', 'Avatar Press',
                      'Abstract Studios','Archie Comics', 'Vertigo',
                      'Valiant Comics']

    SUPPORTED_DIAMOND_PUBS = ['MARVEL COMICS', 'DC COMICS', 'DARK HORSE COMICS',
                              'IDEA & DESIGN WORKS LLC', 'BOOM ENTERTAINMENT',
                              'IMAGE COMICS', 'DYNAMIC FORCES',
                              'ABSTRACT STUDIOS', 'AVATAR PRESS INC',
                              'ARCHIE COMIC PUBLICATIONS', 'IDW PUBLISHING',
                              'VALIANT ENTERTAINMENT LLC']

    # Flask Application Configuration
    SECRET_KEY = environ['SECRET_KEY']

    # URIS
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
    SECURITY_RECOVERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_SEND_REGISTER_EMAIL = True
    #SECURITY_CONFIRMABLE = True
    #SECURITY_LOGIN_WITHOUT_CONFIRMATION = True

    # SECURITY_POST_CONFIRM_VIEW = '/set_something_up'

    SECURITY_TRACKABLE = True
    SECURITY_POST_LOGIN_URL = '/'

    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = environ['SECURITY_PASSWORD_SALT']
    SECURITY_REMEMBER_SALT = environ['SECURITY_REMEMBER_SALT']
    SECURITY_RESET_SALT = environ['SECURITY_RESET_SALT']
    SECURITY_RESET_WITHIN = '5 days'
    #SECURITY_CONFIRM_WITHIN = '5 days'

    SECURITY_EMAIL_SENDER = 'no-reply@longboxed.com'
    SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome to Longboxed!'
    #SECURITY_EMAIL_SUBJECT_CONFIRM = 'Please confirm your Longboxed email!'

    # Mail configuration
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USERNAME = environ['MAIL_USERNAME']
    MAIL_PASSWORD = environ['MAIL_PASSWORD']

    BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT = environ['BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT']

    SOCIAL_GOOGLE = {
        'consumer_key': environ['GOOGLE_CONSUMER_KEY'],
        'consumer_secret': environ['GOOGLE_CONSUMER_SECRET'],
        'request_token_params': {
            'scope': 'openid email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar'
        }
    }

    SOCIAL_FACEBOOK = {
        'consumer_key': environ['FACEBOOK_CONSUMER_KEY'],
        'consumer_secret': environ['FACEBOOK_CONSUMER_SECRET']
    }

    SOCIAL_TWITTER = {
        'consumer_key': environ['TWITTER_CONSUMER_KEY'],
        'consumer_secret': environ['TWITTER_CONSUMER_SECRET']
    }

    @staticmethod
    def init_app(app, **kwargs):
        pass


class ProdConfig(Config):
    """Production Configuration"""
    CONFIG_NAME = 'production'
    DEBUG = False
    USE_AWS = True
    CACHE_CONFIG = {'CACHE_TYPE': 'simple'}

    @classmethod
    def init_app(cls, app, **kwargs):
        Config.init_app(app)

    @classmethod
    def get_store(cls):
        store = S3Store(
                cls.AWS_S3_BUCKET,
                cls.AWS_ACCESS_KEY_ID,
                cls.AWS_SECRET_KEY
        )
        return store


class StagingConfig(ProdConfig):
    """Staging Configuration"""
    CONFIG_NAME = 'staging'

    @classmethod
    def init_app(cls, app, **kwargs):
        ProdConfig.init_app(app)

    @classmethod
    def get_store(cls):
        store = ProdConfig.get_store()
        return store


class DevConfig(Config):
    """Development Configuration"""
    CONFIG_NAME = 'development'
    DEBUG = True
    USE_AWS = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_CONFIG = {'CACHE_TYPE': 'simple'}

    @classmethod
    def init_app(cls, app, **kwargs):
        Config.init_app(app)
        store = kwargs.get('store')
        app.wsgi_app = store.wsgi_middleware(app.wsgi_app)

    @classmethod
    def get_store(cls):
        store = HttpExposedFileSystemStore('store', 'images')
        return store


config = {
    'dev': DevConfig,
    'stag': StagingConfig,
    'prod': ProdConfig,

    'default': DevConfig
}
