# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""

from flask.ext.script import Command

from ..services import comics


class UpdateDatabaseCommand(Command):
    """Updates database with TFAW Daily Download"""

    def run(self):
        print 'Starting update'
        comics.add_new_issues_to_database()
        print 'Done Adding to DB'


class ScheduleReleasesCommand(Command):
    """Automatically schedule releases from Diamond Release file"""
    
    def run(self):
        print 'Starting scheduling'
        content = comics.get_shipping_this_week()
        shipping = comics.get_diamond_ids_shipping(content)
        comics.compare_shipping_with_database(shipping)
        print 'Done Scheduling'