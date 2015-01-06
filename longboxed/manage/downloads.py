# -*- coding: utf-8 -*-
"""
    longboxed.manage.downloads
    ~~~~~~~~~~~~~~~~~~~~~~~

    download management commands
"""
from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool

from ..models import DiamondList, User, Bundle
from ..helpers import week_handler, is_int


class DownloadScheduleBundleCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week',
                   required=True,
                   choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        diamond_list = DownloadDiamondListCommand().run(week)
        if diamond_list:
            NewScheduleReleasesCommand().run(diamond_list=diamond_list)


class DownloadDiamondListCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week',
                   required=True,
                   choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        date = week_handler(week)
        f = current_app.config.get('RELEASE_CSV_RULES')
        f = [x[2] for x in f]
        sp = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
        diamond_list= DiamondList.download_and_process(week, f, sp)
        return diamond_list


class NewScheduleReleasesCommand(Command):
    def get_options(self):
        return [
                Option('-m', '--md5', dest='md5', required=True),
                Option('-d', '--date', dest='date')
        ]
    def run(self, md5=None, date=None, diamond_list=None):
        if not diamond_list:
            s = md5+'%%'
            diamond_lists = DiamondList.query.filter(
                                                DiamondList.hash_string.ilike(s))\
                                             .all()
            if diamond_lists:
                if len(diamond_lists) > 1:
                    print 'Found %i diamond lists matching md5 hash \'%s\'' % (
                            len(diamond_lists), md5)
                    for i, l in enumerate(diamond_lists):
                        print '\t%i: %s' % (i, l)
                    choice = prompt(
                            'Please choose the correct diamond list (or\'none\')')
                    if choice:
                        if is_int(choice):
                            choice = int(choice)
                            diamond_list = diamond_lists[choice]
                            date = date or diamond_list.date
                            ds = date.strftime('%Y-%m-%d')
                            print 'Releasing %s on date %s' % (diamond_list, ds)
                            prompt_string = 'Are you sure?'
                            x = prompt_bool(prompt_string)
                            print x
                        else:
                            print 'Choice must be a number! Aborting...'
            else:
                print 'No diamond lists matching md5 hash \'%s\'' % md5
        if diamond_list:
            date = date or diamond_list.date
            ds = date.strftime('%Y-%m-%d')
            print 'Releasing %s on date %s' % (diamond_list, ds)
            diamond_list.release_issues(date)


class NewBundleIssuesCommand(Command):
    """Creates bundles for users"""
    def get_options(self):
        return [
                Option('-w', '--week', dest='week',
                       required=True,
                        choices=['thisweek', 'nextweek', 'twoweeks']),
        ]
    def run(self, week, issues=[]):
        date = week_handler(week)
        for user in User.query.all():
            matches = [i for i in issues
                       if i.title in user.pull_list and i.is_parent]
            Bundle.refresh_user_bundle(user, date, matches)

