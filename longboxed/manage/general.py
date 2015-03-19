# -*- coding: utf-8 -*-
"""
    longboxed.manage.general
    ~~~~~~~~~~~~~~~~~~~~~~~

    general longboxed management commands
"""
from flask.ext.script import Command, prompt_bool

from ..core import cache
from ..models import Issue


class ClearCacheCommand(Command):
    def run(self, proceed=False):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting: Clearing Cache     '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        if proceed or prompt_bool('Are you sure you want to clear the cache?'):
            cache.clear()
            print 'Cache cleared!'
        else:
            print 'Cache not cleared. Aborting...'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


