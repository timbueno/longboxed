# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool
from flask.ext.security.utils import verify_password

from ..core import db
from ..importer import NewDailyDownloadImporter, NewWeeklyReleasesImporter
from ..models import (Issue, IssueCover, issues_creators, issues_bundles,
                      User)


class TestCommand(Command):
    def run(self):
        pass


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


class CleanCoverImages(Command):
    """Removes TFAW "Image Not Available" cover images"""
    def run(self):
        print 'Cleaning cover images...'
        print '~~~~~~~~~~~~~~~~~~~~~~~~'
        total_count = Issue.query.count()
        total_processed = 0
        for issue in Issue.query.all():
            if total_processed % 50 == 0:
                print 'Proccessed %i/%i issues...' % (total_processed, total_count)
            total_processed = total_processed+1
            with open('media/tfaw_nocover.jpg') as f:
                compare_bytes = f.read()
            if issue.check_cover_image(compare_bytes):
                print "Removing cover image for %s" % issue.complete_title
        print 'Done!'


class DeleteAllIssues(Command):
    def run(self):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print 'WARNING!!!!! YOU ARE ABOUT TO DELETE ALL ISSUES!!!!!'
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        c = prompt_bool('Are you sure you wish to continue?')
        if c:
            email = prompt('Enter your administrator email address: ')
            u = User.query.filter_by(email=email).first()
            if u and u.has_role('super'):
                password = prompt('Enter password: ')
                if verify_password(password, u.password):
                    print 'Deleting `issue_creators` table'
                    db.engine.execute(issues_creators.delete())
                    print 'Deleting `issues_bundles` table'
                    db.engine.execute(issues_bundles.delete())
                    print 'Deleting `Issue Covers` table'
                    IssueCover.query.delete()
                    print 'Deleting all objects from `Issues` table'
                    Issue.query.delete()
                    db.session.commit()
                    print 'All Issues have been deleted.'
                    print 'You should delete the cover images from the store!'
                else:
                    print 'Incorrect password, Aborting...'
            else:
                print 'User not found or is not an administrator, Aborting...'
        else:
            print 'Aborting...'
            return
