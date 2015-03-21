# -*- coding: utf-8 -*-
"""
    longboxed.manage.general
    ~~~~~~~~~~~~~~~~~~~~~~~

    general longboxed management commands
"""
import twitter

from flask import current_app, url_for
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
        # Set up the api
        kwargs = current_app.config.get('TWITTER')
        api = twitter.Api(**kwargs)

        # Build the tweet
        issue = Issue.featured_issue(current_wednesday())
        text = 'Featured This Week: %s\n' % issue.complete_title
        f = issue.get_cover_image_file()
        link = url_for(
                'comics.issue',
                diamond_id=issue.diamond_id,
                _external=True)
        tweet = text + link

        # Tweet the featured issue
        print tweet
        status = api.PostMedia(status=tweet, media=f)


