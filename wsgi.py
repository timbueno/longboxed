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

application = DispatcherMiddleware(frontend.create_app(os.getenv('APP_ENV') or 'default'), {
    '/api/v1': api_v1.create_app(os.getenv('APP_ENV') or 'default')
})

if __name__ == "__main__":
    run_simple('0.0.0.0', 3000, application, use_reloader=True, use_debugger=True)
