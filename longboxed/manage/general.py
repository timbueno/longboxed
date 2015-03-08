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


class CloneDiamondIdCommand(Command):
    def run(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting: Cloning Diamond Ids '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        if prompt_bool('Are you sure you want to clone \'diamond_id\' to '\
                       '\'old_diamond_id\'?'):
            pagination = Issue.query.paginate(1, per_page=50, error_out=False)
            has_next = True
            while has_next:
                for issue in pagination.items:
                    issue.old_diamond_id = issue.diamond_id
                    issue.save()
                if pagination.page:
                    percent_complete = (pagination.page/float(pagination.pages)) * 100.0
                    print '%.2f%% complete...' % percent_complete
                if pagination.has_next:
                    pagination = pagination.next(error_out=False)
                else:
                    has_next = False
        else:
            print 'Diamond IDs were NOT cloned. Aborting...'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


