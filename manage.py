# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~

    Manager module
"""
import os

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from longboxed.core import db
from longboxed.frontend import create_app
from longboxed.models import (User, Issue, Title, Publisher, Bundle, Role,
                              DiamondList)
from longboxed.manage import (CreateNewRoleCommand, CreateDefaultRolesCommand,
                             CreateUserCommand, AddSuperUserRoleCommand,
                             ListUsersCommand, ListRolesCommand,
                             TestCommand, ImportDatabase, DeleteAllIssues,
                             SetCoverImageCommand, ScheduleReleasesCommand,
                             CleanCoverImages, DownloadScheduleBundleCommand,
                             BundleIssuesCommand, DownloadDiamondListCommand,
                             ClearCacheCommand, RemovePublisherTitleFromPullLists)


app = create_app(os.getenv('APP_ENV') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def _make_shell_context():
    return dict(app=app, db=db, User=User, Issue=Issue,
                Title=Title, Publisher=Publisher, Bundle=Bundle,
                Role=Role, DiamondList=DiamondList)
manager.add_command("shell", Shell(make_context=_make_shell_context))
manager.add_command('db', MigrateCommand)

manager.add_command('test', TestCommand())

# Application management commands
manager.add_command('clear_cache', ClearCacheCommand())

# User Commands
manager.add_command('create_role', CreateNewRoleCommand())
manager.add_command('create_roles', CreateDefaultRolesCommand())
manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_super_role', AddSuperUserRoleCommand())
manager.add_command('list_users', ListUsersCommand())
manager.add_command('list_roles', ListRolesCommand())

# Comic Book Management Commands
manager.add_command('import_database', ImportDatabase())
manager.add_command('download_diamond_list', DownloadDiamondListCommand())
manager.add_command('schedule_releases', ScheduleReleasesCommand())
manager.add_command('bundle_issues', BundleIssuesCommand())
manager.add_command('download_schedule_bundle', DownloadScheduleBundleCommand())
manager.add_command('delete_all_issues', DeleteAllIssues())
manager.add_command('set_cover_image', SetCoverImageCommand())
manager.add_command('clean_cover_images', CleanCoverImages())
manager.add_command('remove_publisher_title_from_pull_lists',
                    RemovePublisherTitleFromPullLists())


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade

    print 'Running deployment tasks...'

    # Migrate database to latest revision
    print 'Migrating database to latest revison...',
    upgrade()
    print 'done'

    print 'Checking for user roles...',
    Role.insert_roles()
    print 'done'

    print 'Checking for Publisher images...'
    Publisher.set_images()
    print 'done'

    if app.config.get('APP_ENV') in ('prod', 'stag'):
        print 'Uploading Static assets to S3...'
        import flask_s3
        flask_s3.create_all(app)
        print 'done'
    else:
        print 'NOT uploading assets to S3, on dev...'


if __name__ == '__main__':
    # Run the manager
    manager.run()
