# -*- coding: utf-8 -*-
"""
    longboxed.manage.general
    ~~~~~~~~~~~~~~~~~~~~~~~

    general longboxed management commands
"""
import twitter

from flask import current_app
from flask.ext.script import Command, prompt_bool

from ..core import cache
from ..helpers import current_wednesday
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


class TweetFeaturedIssueCommand(Command):
    def run(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting: Tweeting Featured   '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        # Set up the api
        kwargs = current_app.config.get('TWITTER')
        api = twitter.Api(**kwargs)

        # Build the tweet
        issue = Issue.featured_issue(current_wednesday())
        text = 'Featured This Week: %s\n' % issue.complete_title
        f = issue.get_cover_image_file()
        domain = current_app.config.get('LB_DOMAIN_NAME', 'longboxed.com')
        link = domain + '/issue/%s' % issue.diamond_id
        tweet = text + link

        # Tweet the featured issue
        print tweet
        status = None
        if f:
            status = api.PostMedia(status=tweet, media=f)
        else:
            status = api.PostUpdate(status=tweet)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        return status

