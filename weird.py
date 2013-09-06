# Directory structure:

# web_app/
# web_app/locale/
# web_app/templates/
# web_app/static/
# web_app/sample_app.py
# web_app/views.py
# web_app/run_debug.py
# web_app/run_production.py
# web_app/common.ini
# web_app/development.ini
# web_app/production.ini
# The file 'common.ini' contains some common configuration:

LOGGER_NAME = 'sample_app'
LOGGING_CONFIG = { 
	'version': 1, 
	'formatters': { 
		'long': {
			'format': '%(asctime)s %(levelname)-5.5s [%(name)s][%(threadName)s] %(message)s'
		},
		'short': {
			'format': '%(message)s'
		}
	}, 
	'handlers': {
		'console': { 
			'class': 'logging.StreamHandler', 
			'formatter': 'short',
			'stream': 'ext://sys.stderr'
		}, 
		'file': { 
			'class': 'logging.handlers.RotatingFileHandler',
			'formatter': 'long', 
			'filename': 'sample_app.log',
			'maxBytes': 16384,
			'backupCount': 5
		}
	}, 
	'loggers': { 
		'sample_app': {
			'level': 'DEBUG'
		},
		'sqlalchemy.engine': {
			'propagate': True
		},
		'werkzeug': {
			'propagate': True
		}
	}, 
	'root': {
		'level': 'INFO',
		'handlers': ['console']
	}
}

# Here is 'development.ini':

DEBUG = True SQLALCHEMY_DATABASE_URI = \ 'sqlite:///development.db'

# And here is 'production.ini':

!python DEBUG = False SQLALCHEMY_DATABASE_URI = \ 'mysql://username:password@server/db'

# The 'sample_app.py' file:

from logging.config import dictConfig
from flask import Flask
from flaskext.babel import Babel
from flaskext.sqlalchemy import SQLAlchemy

app = None
babel = None
db = None

def make_app(config_files=None,\ logging_config_callback=None):

	global app, babel, db
	app = Flask(__name__)
	app.config.from_pyfile('common.ini')

	if config_files:
		for conf in config_files:
			app.config.from_pyfile(conf)

	logging_config = app.config['LOGGING_CONFIG']
	if callable(logging_config_callback):
		logging_config_callback(logging_config)

	dictConfig(logging_config)

	# Setup extensions 
	babel = Babel(app)
	db = SQLAlchemy(app)
	Since the app object is created
	we can import our views module
	that depends on the 'app.route'
	decorator from .views import *
	return app

# The 'logging_config_callback' parameter can be used to modify logging configuration. 
# 'config_files' can be used to add a list of additional configuration files 
# specific to some deployment.

# Here is run_debug.py:

!/usr/bin/env python
import sample_app
app = sample_app.make_app(config_files='development.ini',))
app.run(host='127.0.0.1', port=8080)

# and run_production.py:

!/usr/bin/env python
import sample_app
app = sample_app.make_app(config_files='production.ini',))
app.run(host='0.0.0.0', port=80)