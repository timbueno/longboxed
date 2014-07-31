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
from longboxed.models import User, Issue, Title, Publisher, Bundle
from longboxed.manage import CreateNewRoleCommand, CreateDefaultRolesCommand, CreateUserCommand, \
                             AddSuperUserRoleCommand, ListUsersCommand, ListRolesCommand, \
                             ScheduleReleasesCommand, \
                             TestCommand, SetCoverImageCommand, UserBundlesCommand, ImportDatabase


app = create_app(os.getenv('APP_ENV') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def _make_shell_context():
    return dict(app=app, db=db, User=User, Issue=Issue,
                Title=Title, Publisher=Publisher, Bundle=Bundle)
manager.add_command("shell", Shell(make_context=_make_shell_context))
manager.add_command('db', MigrateCommand)

manager.add_command('create_role', CreateNewRoleCommand())
manager.add_command('create_roles', CreateDefaultRolesCommand())
manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_super_role', AddSuperUserRoleCommand())
manager.add_command('list_users', ListUsersCommand())
manager.add_command('list_roles', ListRolesCommand())
manager.add_command('schedule_releases', ScheduleReleasesCommand())
manager.add_command('import_database', ImportDatabase())
manager.add_command('set_cover_image', SetCoverImageCommand())
manager.add_command('bundle_issues', UserBundlesCommand())
manager.add_command('test', TestCommand())

if __name__ == '__main__':
    manager.run()