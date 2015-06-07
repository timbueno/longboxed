# -*- coding: utf-8 -*-
"""
    longboxed.manage.users
    ~~~~~~~~~~~~~~~~~~~~~

    user management commands
"""
from flask import current_app
from flask.ext.script import Command, Option, prompt, prompt_pass
from flask.ext.security.forms import RegisterForm
from flask.ext.security.registerable import register_user
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy

from ..core import db
from ..models import User, Role, Publisher


class RemovePublisherTitleFromPullLists(Command):
    """
    Removes all instances of titles by a certain publisher from all users pull
    lists
    """
    def get_options(self):
        return [
                Option('-p', '--publisher', dest='publisher', required=True),
        ]

    def run(self, publisher=None):
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        print '!! Starting: Removing all \'%s\' titles from users pull lists' % publisher
        print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
        if Publisher.query.filter_by(name=publisher).first():
            pagination = User.query.paginate(1, per_page=20, error_out=False)
            has_next = True
            while has_next:
                for user in pagination.items:
                    save_user = False
                    for title in user.pull_list:
                        if title.publisher.name == publisher:
                            print 'Removing %s from %s\'s pull list...' % (title.name, user.email)
                            save_user = True
                            user.pull_list.remove(title)
                    if save_user:
                        user.save()
                if pagination.page:
                    percent_complete = (pagination.page/float(pagination.pages)) * 100.0
                    print '%.2f%% complete...' % percent_complete
                if pagination.has_next:
                    pagination = pagination.next(error_out=False)
                else:
                    has_next = False
        else:
            print 'Publisher \'%s\' not found' % publisher


class CreateNewRoleCommand(Command):
    """Creates a role"""

    def run(self):
        name = prompt('Role Name')
        description = prompt('Role Description')
        _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
        _security_datastore.create_role(name=name, description=description)
        db.session.commit()
        return


class CreateDefaultRolesCommand(Command):
    """Creates inital roles (user, admin, super)"""

    def run(self):
        default_roles = [('user', 'No Permissions'), ('admin', 'Comic specific permissions'), ('super', 'All permissions')]
        _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
        for role in default_roles:
            _security_datastore.find_or_create_role(name=role[0], description=role[1])
            db.session.commit()
        print 'Sucessfully added roles'


class CreateUserCommand(Command):
    """Create a user"""

    def run(self):
        email = prompt('Email')
        password = prompt_pass('Password')
        password_confirm = prompt_pass('Confirm Password')
        data = MultiDict(dict(email=email, password=password, password_confirm=password_confirm))
        form = RegisterForm(data, csrf_enabled=False)
        if form.validate():
            user = register_user(email=email, password=password)
            print '\nUser created successfully'
            print 'User(id=%s email=%s' % (user.id, user.email)
            return
        print '\nError creating user:'
        for errors in form.errors.values():
            print '\n'.join(errors)


class AddSuperUserRoleCommand(Command):
    """Gives the given user SuperUser role"""

    def run(self):
        email = prompt('Email')
        # user = users.first(email=email)
        user = User.query.filter_by(email=email).first()
        if user:
            _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
            admin_role = _security_datastore.find_role('admin')
            super_role = _security_datastore.find_role('super')
            _security_datastore.add_role_to_user(user, super_role)
            _security_datastore.add_role_to_user(user, admin_role)
            db.session.commit()
            print '\nUser given super role sucessfully'
            return
        print '\nNo user found'


class AddAdminUserRoleCommand(Command):
    """Gives the given user admin role"""

    def run(self):
        email = prompt('Email')
        # user = users.first(email=email)
        user = User.query.filter_by(email=email).first()
        if user:
            _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
            admin_role = _security_datastore.find_role('admin')
            _security_datastore.add_role_to_user(user, admin_role)
            db.session.commit()
            print '\nUser given admin role sucessfully'
            return
        print '\nNo user found'


class ListRolesCommand(Command):
    """List all roles"""

    def run(self):
        for r in Role.query.all():
            print 'Role(name=%s description=%s)' % (r.name, r.description)
        # for r in roles.all():
        #     print 'Role(name=%s description=%s)' % (r.name, r.description)


class ListUsersCommand(Command):
    """List all users"""

    def run(self):
        for u in User.query.all():
            print 'User(id=%s email=%s)' % (u.id, u.email)
        # for u in users.all():
        #     print 'User(id=%s email=%s)' % (u.id, u.email)
