# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool

from ..importer import NewDailyDownloadImporter, NewWeeklyReleasesImporter
from ..models import Issue


class TestCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        fieldnames = [x[2] for x in current_app.config['RELEASE_CSV_RULES']]
        issue_releaser = NewWeeklyReleasesImporter()
        issue_releaser.run(
            csv_fieldnames = fieldnames,
            supported_publishers = current_app.config['SUPPORTED_DIAMOND_PUBS'],
            affiliate_id = current_app.config['AFFILIATE_ID'],
            week = week
        )
        return
        

class ScheduleReleasesCommand(Command):
    def get_options(self):
        return [
            Option('-w', '--week', dest='week', required=True, choices=['thisweek', 'nextweek', 'twoweeks']),
        ]

    def run(self, week):
        fieldnames = [x[2] for x in current_app.config['RELEASE_CSV_RULES']]
        issue_releaser = NewWeeklyReleasesImporter()
        issue_releaser.run(
            csv_fieldnames = fieldnames,
            supported_publishers = current_app.config['SUPPORTED_DIAMOND_PUBS'],
            affiliate_id = current_app.config['AFFILIATE_ID'],
            week = week
        )
        return


class ImportDatabase(Command):
    def get_options(self):
        return [
            Option('--days', '-d', dest='days', default=21, type=int)
        ]

    def run(self, days):
        fieldnames = [x[2] for x in current_app.config['CSV_RULES']]
        database_importer = NewDailyDownloadImporter()
        database_importer.run(
            csv_fieldnames = fieldnames,
            supported_publishers = current_app.config['SUPPORTED_PUBS'],
            affiliate_id = current_app.config['AFFILIATE_ID'],
            thumbnail_widths = current_app.config['THUMBNAIL_WIDTHS'],
            days = days
        )
        return


class SetCoverImageCommand(Command):
    """
    Sets the cover image of an issue. The issues is found in the 
    database with a diamond id. If the issue already has an image
    attached, you can optionally choose to replace it.
    """
    def run(self):
        diamond_id = prompt('Issue Diamond id')
        issue = Issue.query.filter_by(diamond_id=diamond_id).first()
        if issue:
            url = prompt('Url of jpg image for cover image')
            overwrite = False
            if issue.cover_image.original:
                print 'Issue object already has a cover image set.'
                overwrite = prompt_bool('Overwrite existing picture?')
            success = issue.set_cover_image_from_url(url, overwrite=overwrite)
            if success:
                print 'Successfully set cover image'
            return
        print 'No issue found!'
        return