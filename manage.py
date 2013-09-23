# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~

    Manager module
"""

from flask.ext.script import Manager

from longboxed.api import create_app
from longboxed.manage import CreateNewRoleCommand, CreateDefaultRolesCommand, CreateUserCommand, \
                             AddSuperUserRoleCommand, ListUsersCommand, ListRolesCommand, \
                             UpdateDatabaseCommand, ScheduleReleasesCommand

manager = Manager(create_app())
manager.add_command('create_role', CreateNewRoleCommand())
manager.add_command('create_roles', CreateDefaultRolesCommand())
manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_super_role', AddSuperUserRoleCommand())
manager.add_command('list_users', ListUsersCommand())
manager.add_command('list_roles', ListRolesCommand())

manager.add_command('update_database', UpdateDatabaseCommand())
manager.add_command('schedule_releases', ScheduleReleasesCommand())

if __name__ == '__main__':
    manager.run()