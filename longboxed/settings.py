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
    APP_ENV = environ.get('APP_ENV', 'dev')
    LB_DOMAIN_NAME = environ.get('LB_DOMAIN_NAME', 'longboxed.com')
    USE_S3 = False

    CACHE_CONFIG = {'CACHE_TYPE': 'simple',
                    'CACHE_DEFAULT_TIMEOUT': 30}

    THUMBNAIL_WIDTHS = [100, 250, 500]

    # Longboxed Specific Variables
    AFFILIATE_ID = environ['AFFILIATE_ID']
    COMPARISON_IMAGE = 'media/tfaw_nocover.jpg'
    COMPARISON_IMAGE_URL = 'http://affimg.tfaw.com/covers_tfaw/400/no/nocover.jpg'
    DISABLED_PUBS = ['default_placeholder']
    SUPPORTED_PUBS = ['Marvel Comics', 'DC Comics', 'Dark Horse',
                      'IDW Publishing', 'Boom! Studios', 'Image Comics',
                      'Dynamite Entertainment', 'Avatar Press',
                      'Abstract Studios', 'Archie Comics', 'Vertigo',
                      'Valiant Comics']

    SUPPORTED_DIAMOND_PUBS = ['MARVEL COMICS', 'DC COMICS', 'DARK HORSE COMICS',
                              'IDEA & DESIGN WORKS LLC', 'BOOM ENTERTAINMENT',
                              'IMAGE COMICS', 'DYNAMIC FORCES',
                              'ABSTRACT STUDIOS', 'AVATAR PRESS INC',
                              'ARCHIE COMIC PUBLICATIONS', 'IDW PUBLISHING',
                              'VALIANT ENTERTAINMENT LLC']

    DIAMOND_LIST_FIXES = {
            'ANGEL AND FAITH SEASON 10': 'Angel and Faith: Season Ten',
            'HELLBOY AND THE BPRD': 'Hellboy and the B.P.R.D.: 1952',
            'PASTAWAYS': 'Past Aways'
    }

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

    SECURITY_TRACKABLE = True
    SECURITY_POST_LOGIN_URL = '/'

    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_PASSWORD_SALT = environ['SECURITY_PASSWORD_SALT']
    SECURITY_REMEMBER_SALT = environ['SECURITY_REMEMBER_SALT']
    SECURITY_RESET_SALT = environ['SECURITY_RESET_SALT']
    SECURITY_RESET_WITHIN = '5 days'

    SECURITY_EMAIL_SENDER = 'no-reply@longboxed.com'
    SECURITY_EMAIL_SUBJECT_REGISTER = 'Welcome to Longboxed!'

    # Mail configuration
    MAIL_SERVER = 'smtp.mailgun.org'
    MAIL_PORT = 587
    MAIL_USERNAME = environ['MAIL_USERNAME']
    MAIL_PASSWORD = environ['MAIL_PASSWORD']

    BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT = environ['BOOTSTRAP_GOOGLE_ANALYTICS_ACCOUNT']

    IOS_APP_URL = 'https://itunes.apple.com/us/app/longboxed/id965045339?ls=1&mt=8'
    IOS_APP_ID = '965045339'

    SOCIAL_GOOGLE = {
        'consumer_key': environ['GOOGLE_CONSUMER_KEY'],
        'consumer_secret': environ['GOOGLE_CONSUMER_SECRET'],
        'request_token_params': {
            'scope': 'openid email https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/calendar'
        }
    }

    #FACEBOOK = {
        #'consumer_key': environ['FACEBOOK_CONSUMER_KEY'],
        #'consumer_secret': environ['FACEBOOK_CONSUMER_SECRET']
    #}

    TWITTER = {
        'consumer_key': environ.get('TWITTER_CONSUMER_KEY', ''),
        'consumer_secret': environ.get('TWITTER_CONSUMER_SECRET', ''),
        'access_token_key': environ.get('LB_TWITTER_ACCESS_TOKEN', ''),
        'access_token_secret': environ.get('LB_TWITTER_TOKEN_SECRET', '')
    }

    @staticmethod
    def init_app(app, **kwargs):
        pass


class ProdConfig(Config):
    """Production Configuration"""
    S3_BUCKET_NAME = environ.get('S3_BUCKET_NAME')
    AWS_ACCESS_KEY_ID = environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = environ.get('AWS_SECRET_ACCESS_KEY')

    CONFIG_NAME = 'production'
    DEBUG = False
    USE_S3 = True

    CACHE_CONFIG = {'CACHE_TYPE': 'memcached',
                    'CACHE_MEMCACHED_SERVERS': [environ['MEMCACHE_SCHEME']],
                    'CACHE_DEFAULT_TIMEOUT': int(environ['MEMCACHE_DEFAULT_TIMEOUT'])
                   }

    @classmethod
    def init_app(cls, app, **kwargs):
        Config.init_app(app)

    @classmethod
    def get_store(cls):
        store = S3Store(
                cls.S3_BUCKET_NAME,
                cls.AWS_ACCESS_KEY_ID,
                cls.AWS_SECRET_ACCESS_KEY
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
    USE_S3 = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_CONFIG = {'CACHE_TYPE': 'memcached',
                    'CACHE_MEMCACHED_SERVERS': [environ['MEMCACHE_SCHEME']],
                    'CACHE_DEFAULT_TIMEOUT': int(environ['MEMCACHE_DEFAULT_TIMEOUT'])
                   }

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
