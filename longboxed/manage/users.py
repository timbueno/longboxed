# -*- coding: utf-8 -*-
"""
    longboxed.manage.users
    ~~~~~~~~~~~~~~~~~~~~~

    user management commands
"""
from flask import current_app
from flask.ext.script import Command, prompt, prompt_pass
from flask.ext.security.forms import RegisterForm
from flask.ext.security.registerable import register_user
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy

from ..core import db
from ..helpers import current_wednesday
from ..models import Issue, User, Role, Bundle


class UserBundlesCommand(Command):
    """
    Creates bundles for each user
    """
    def run(self):
        date = current_wednesday()
        issues_this_week = Issue.query.filter(
                                        Issue.on_sale_date==date,
                                        Issue.is_parent==True).all()
        for user in User.query.all():
            matches = [i for i in issues_this_week if i.title in user.pull_list and i.is_parent]
            Bundle.refresh_user_bundle(user, date, matches)
        return


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