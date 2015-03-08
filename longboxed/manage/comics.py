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
from ..importer import DailyDownloadImporter
from ..models import (DiamondList, Issue, IssueCover, issues_creators, issues_bundles,
                      User)
import re


class TestCommand(Command):
    def run(self):
        supported_publishers = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
        fieldnames = [c[2] for c in current_app.config.get('RELEASE_CSV_RULES')]
        diamond_list = DiamondList.query\
                                  .filter_by(hash_string='a4084c91829c3d826c93b9954fed1e75')\
                                  .first()
        data = diamond_list.process_csv(fieldnames)
        failed_rows = {}
        for row in data:
            if Issue.check_release_relevancy(row, supported_publishers):
                issue = Issue.query.filter_by(diamond_id=row['diamond_id']).first()
                if issue:
                    # Process issue
                    pass
                else:
                    try:
                        m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', row['complete_title']).groupdict()
                        matched_tuple = (m['issue_number'], m['title'])
                        if matched_tuple in failed_rows.keys():
                            failed_rows[matched_tuple].append(row)
                        else:
                            failed_rows[matched_tuple] = [row]
                    except Exception, err:
                        print err
        for key in failed_rows.keys():
            diamond_list_fixes = current_app.config['DIAMOND_LIST_FIXES']
            if diamond_list_fixes.get(key[1]):
                fixed_name = diamond_list_fixes[key[1]]
                print 'FIX MATCH! - %s : %s' % (key[1], fixed_name)
                failed_rows[(key[0], fixed_name)] = failed_rows.pop(key)
        for key in failed_rows.keys():
            complete_title = key[1]
            issue = Issue.query\
                          .filter(
                            Issue.complete_title.ilike('%'+complete_title.replace(' ', '%%')+'%'),
                            Issue.issue_number==key[0],
                            Issue.is_parent==True)\
                          .first()
            if issue:
                if issue.diamond_id.isnumeric():
                    # Replace queried issue diamond_id with issue.diamond_id
                    print key, issue.complete_title, issue.diamond_id, failed_rows[key][0]['diamond_id']



class ImportDatabase(Command):
    def get_options(self):
        return [
            Option('--days', '-d', dest='days', default=21, type=int)
        ]

    def run(self, days):
        fieldnames = [x[2] for x in current_app.config['CSV_RULES']]
        database_importer = DailyDownloadImporter()
        database_importer.run(
            csv_fieldnames = fieldnames,
            supported_publishers = current_app.config['SUPPORTED_PUBS'],
            affiliate_id = current_app.config['AFFILIATE_ID'],
            thumbnail_widths = current_app.config['THUMBNAIL_WIDTHS'],
            days = days,
            comparison_image = current_app.config['COMPARISON_IMAGE']
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
        total_cleaned = 0
        thumbs = current_app.config.get('THUMBNAIL_WIDTHS')
        for issue in Issue.query.all():
            if total_processed % 50 == 0:
                print 'Proccessed %i/%i issues...' % (total_processed, total_count)
            total_processed = total_processed+1
            with open('media/tfaw_nocover.jpg') as f:
                compare_bytes = f.read()
            if issue.check_cover_image(compare_bytes):
                print "Removing cover image for %s" % issue.complete_title
                issue.remove_cover_image(thumbs)
                total_cleaned = total_cleaned + 1
        print 'Done!'
        print 'Cleaned %i issue covers' % total_cleaned


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
