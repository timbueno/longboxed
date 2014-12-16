# -*- coding: utf-8 -*-
"""
    longboxed.manage.downloads
    ~~~~~~~~~~~~~~~~~~~~~~~

    download management commands
"""
from flask import current_app
from flask.ext.script import Command, Option

from ..models import DiamondList


class NewNewScheduleReleasesCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week',
                   required=True,
                   choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        f = current_app.config.get('RELEASE_CSV_RULES')
        f = [x[2] for x in f]
        sp = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
        diamond_list = DiamondList.download_and_process(week, f, sp)

        if diamond_list:
            print 'Releasing issues for %s' % diamond_list.date
            diamond_list.release_issues()
