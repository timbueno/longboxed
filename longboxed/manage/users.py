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
from ..services import users


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
        user = users.first(email=email)
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
        user = users.first(email=email)
        if user:
            _security_datastore = LocalProxy(lambda: current_app.extensions['security'].datastore)
            admin_role = _security_datastore.find_role('admin')
            _security_datastore.add_role_to_user(user, admin_role)
            db.session.commit()
            print '\nUser given admin role sucessfully'
            return
        print '\nNo user found'
        

class ListUsersCommand(Command):
    """List all users"""

    def run(self):
        for u in users.all():
            print 'User(id=%s email=%s)' % (u.id, u.email)