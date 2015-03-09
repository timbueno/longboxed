# -*- coding: utf-8 -*-
"""
    longboxed.manage.comics
    ~~~~~~~~~~~~~~~~~~~~~~~

    comic management commands
"""
import re

from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_bool
from flask.ext.security.utils import verify_password
from sqlalchemy import func

from ..core import db
from ..importer import DailyDownloadImporter
from ..models import (DiamondList, Issue, IssueCover, issues_creators,
                      issues_bundles, User, Title)


def process_failed_rows(failed_rows):
    grouped_rows = {}
    fixed_issues = []
    for row in failed_rows:
        # Parse the complete title row into its base parts.
        # Group the rows together based on like titles and issue numbers
        try:
            m = re.match(r'(?P<title>[^#]*[^#\s])\s*(?:#(?P<issue_number>([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?))\s*)?(?:\(of (?P<issues>(\d+))\)\s*)?(?P<other>(.+)?)', row['complete_title']).groupdict()
            matched_tuple = (m['issue_number'], m['title'])
            if matched_tuple in grouped_rows.keys():
                grouped_rows[matched_tuple].append(row)
            else:
                grouped_rows[matched_tuple] = [row]
        except Exception, err:
            print err
    # Some diamond list titles just cannot be matched correctly to the database
    # titles. Run them against a mapping between bum titles and their correctly
    # named database titles.
    for key in grouped_rows.keys():
        diamond_list_fixes = current_app.config['DIAMOND_LIST_FIXES']
        if diamond_list_fixes.get(key[1]):
            fixed_name = diamond_list_fixes[key[1]]
            grouped_rows[(key[0], fixed_name)] = grouped_rows.pop(key)
    # Process the grouped rows. Search the database based on the grouped title
    # and the associated issue number.
    for key in grouped_rows.keys():
        query_string = '%'+key[1].replace(' ', '%%')+'%'
        #issues = Issue.query\
                      #.filter(
                        #Issue.complete_title.ilike(query_string),
                        #Issue.issue_number==key[0])\
                      #.order_by(func.char_length(Issue.complete_title))\
                      #.all()
        issues = Issue.query\
                      .filter(Issue.issue_number==key[0])\
                      .join(Title.issues)\
                      .filter(Title.name.ilike(query_string))\
                      .order_by(func.char_length(Issue.complete_title))\
                      .all()
        if issues:
            issues.sort()
            rows = grouped_rows[key]
            rows.sort(key=lambda row: len(row['complete_title']), reverse=False)
            numeric_issues = []
            for issue in issues:
                if issue.diamond_id.isnumeric():
                    numeric_issues.append(issue)
            for i, issue in enumerate(numeric_issues):
                if i > (len(rows)-1):
                    break
                print 'ID: %s | DB: %s | DL: %s' % (rows[i]['diamond_id'],
                                                  issue.complete_title,
                                                  rows[i]['complete_title'])
                #issue.diamond_id = rows[i]['diamond_id']
                fixed_issues.append(issue)
    return fixed_issues


class TestCommand(Command):
    def run(self):
        supported_publishers = current_app.config.get('SUPPORTED_DIAMOND_PUBS')
        fieldnames = [c[2] for c in current_app.config.get('RELEASE_CSV_RULES')]
        diamond_list = DiamondList.query\
                                  .filter_by(hash_string='a4084c91829c3d826c93b9954fed1e75')\
                                  .first()
        data = diamond_list.process_csv(fieldnames)
        failed_rows = []
        issues = []
        for row in data:
            if Issue.check_release_relevancy(row, supported_publishers):
                issue = Issue.query.filter_by(diamond_id=row['diamond_id'])\
                                   .first()
                if issue:
                    # Issue was found, save for later
                    issues.append(issue)
                else:
                    # Row not found for various reasons, add to list for later
                    # processing
                    failed_rows.append(row)
        fixed_issues = process_failed_rows(failed_rows)
        #if fixed_issues:
            #print 'Corrected %d issues!' % len(fixed_issues)
            #for issue in fixed_issues:
                #print issue
        # Combine the lists, set them on the DiamondList model.
        issues = issues + fixed_issues


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
