# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~

    Manager module
"""

from flask.ext.script import Manager

from longboxed.api import create_app
from longboxed.manage import CreateRolesCommand, CreateUserCommand, AddSuperUserRoleCommand, ListUsersCommand

manager = Manager(create_app())
manager.add_command('create_roles', CreateRolesCommand())
manager.add_command('create_user', CreateUserCommand())
manager.add_command('add_super_role', AddSuperUserRoleCommand())
manager.add_command('list_users', ListUsersCommand())

if __name__ == '__main__':
    manager.run()