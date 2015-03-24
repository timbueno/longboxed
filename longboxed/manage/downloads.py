# -*- coding: utf-8 -*-
"""
    longboxed.manage.downloads
    ~~~~~~~~~~~~~~~~~~~~~~~

    download management commands
"""
from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool

from .general import ClearCacheCommand
from ..models import DiamondList, Issue, User, Bundle
from ..helpers import week_handler, is_int


class DownloadScheduleBundleCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week',
                   required=True,
                   choices=['thisweek', 'nextweek', 'twoweeks', 'all']),
        ]

    def run(self, week):
        if week == 'all':
            weeks = ['thisweek', 'nextweek', 'twoweeks']
        else:
            weeks = [week]
        for week in weeks:
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            print '!! Starting: %s' % week
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            diamond_list = DownloadDiamondListCommand().run(week)
            if diamond_list:
                ScheduleReleasesCommand().run(diamond_list=diamond_list)
                issues = diamond_list.issues.all()
                BundleIssuesCommand().run(week=week, issues=issues)
                ClearCacheCommand().run(proceed=True)
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            print '**  Complete: %s' % week
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


class DownloadDiamondListCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week',
                   required=True,
                   choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting: DL Diamond List     '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        f = current_app.config.get('RELEASE_CSV_RULES')
        f = [x[2] for x in f]
        sp = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
        diamond_list = DiamondList.download_and_process(week, f, sp)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        return diamond_list


class ScheduleReleasesCommand(Command):
    def get_options(self):
        return [
                Option('-m', '--md5', dest='md5', required=True),
                Option('-d', '--date', dest='date'),
                Option('-l', '--link', dest='link')
        ]
    def run(self, md5=None, date=None, diamond_list=None, link=False):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting: Releasing Issues     '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

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
                    print 'Found diamond list matching %s' % md5
                    diamond_list = diamond_lists[0]
            else:
                print 'No diamond lists matching md5 hash \'%s\'' % md5
        if diamond_list:
            date = date or diamond_list.date
            if link:
                print 'Linking issues...'
                f = current_app.config.get('RELEASE_CSV_RULES')
                f = [row[2] for row in f]
                sp = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
                diamond_list.link_issues(f, sp)
            diamond_list.release_issues(date)
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


class BundleIssuesCommand(Command):
    """Creates bundles for users"""
    def get_options(self):
        return [
                Option('-w', '--week', dest='week',
                       required=True,
                        choices=['thisweek', 'nextweek', 'twoweeks']),
        ]
    def run(self, week, issues=[]):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'Starting:  User Bundle Routine'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        date = week_handler(week)
        if not issues:
            print 'Querying for issues on %s' % date
            issues = Issue.query.filter_by(on_sale_date=date).all()
        print 'Processing bundles for:'
        print '    date: %s' % date
        print '    user count: %i' % User.query.count()
        pagination = User.query.paginate(1, per_page=20, error_out=False)
        has_next = True
        while has_next:
            for user in pagination.items:
                matches = [i for i in issues
                           if i.title in user.pull_list and i.is_parent]
                Bundle.refresh_user_bundle(user, date, matches)
            if pagination.page:
                percent_complete = (pagination.page/float(pagination.pages)) * 100.0
                print '%.2f%% complete...' % percent_complete
            if pagination.has_next:
                pagination = pagination.next(error_out=False)
            else:
                has_next = False

        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '           Complete           '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


class ReprocessDiamondListsCommand(Command):
    def run(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '!! Reprocessing all DiamondLists'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

        # Get all diamond lists from database.
        dlists = DiamondList.query\
                            .order_by(DiamondList.revision.desc())\
                            .all()
        # Group all diamond lists by like date
        grouped_dlists = {}
        for dlist in dlists:
            if grouped_dlists.get(dlist.date):
                grouped_dlists[dlist.date].append(dlist)
            else:
                grouped_dlists[dlist.date] = [dlist]
        # Iterate over all diamond lists by group. Re-Link all diamond lists and
        # Re-Release only the diamond list with the latest revision. This should
        # be the first list in the iteration.
        dlists_to_release = []
        keys = grouped_dlists.keys()
        keys.sort() # Sort Diamond Lists starting with the earliest
        fieldnames = [x[2] for x in current_app.config.get('RELEASE_CSV_RULES')]
        supported_publishers = current_app.config.get('SUPPORTED_DIAMOND_PUBS')

        print 'Linking all Diamond Lists...'
        for key in keys:
            for i, dlist in enumerate(grouped_dlists[key]):
                print '--------------------------------'
                print 'Linking: %s, Rev: %d' % (dlist.date.strftime('%Y-%m-%d'),
                                                dlist.revision)
                dlist.link_issues(fieldnames, supported_publishers)
                if i == 0:
                    dlists_to_release.append(dlist)
        print '--------------------------------'
        print 'Releasing latest Diamond Lists: %d' % len(dlists_to_release)
        for dlist in dlists_to_release:
            print '--------------------------------'
            dlist.release_issues()

        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '            Complete            '
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'


