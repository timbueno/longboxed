# -*- coding: utf-8 -*-
"""
    wsgi
    ~~~~

    longboxed wsgi module
"""

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from longboxed import api, frontend

application = DispatcherMiddleware(frontend.create_app(), {
    '/api': api.create_app()
})

if __name__ == "__main__":
    run_simple('127.0.0.1', 5000, application, use_reloader=True, use_debugger=True)