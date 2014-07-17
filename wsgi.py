# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    longboxed wsgi module

    APP_ENV must be set as an environment variable.
    Values can be: 
        'prod' for production
        'dev'  for development
"""
import os

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from longboxed import api_v1, frontend
from longboxed.settings import ProdConfig, DevConfig, StagingConfig


if os.environ.get('APP_ENV') == 'prod':
    application = DispatcherMiddleware(frontend.create_app(ProdConfig), {
        '/api/v1': api_v1.create_app(ProdConfig)
    })
elif os.environ.get('APP_ENV') == 'stag':
    application = DispatcherMiddleware(frontend.create_app(StagingConfig), {
        '/api/v1': api_v1.create_app(StagingConfig)
    })
else:
    application = DispatcherMiddleware(frontend.create_app(DevConfig), {
        '/api/v1': api_v1.create_app(DevConfig)
    })

if __name__ == "__main__":
    run_simple('0.0.0.0', 3000, application, use_reloader=True, use_debugger=True)