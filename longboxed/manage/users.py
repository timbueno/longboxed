# -*- coding: utf-8 -*-
"""
    longboxed.manage.users
    ~~~~~~~~~~~~~~~~~~~~~

    user management commands
"""
from datetime import datetime

from flask import current_app, render_template
from flask.ext.script import Command, prompt, prompt_pass
from flask.ext.security.forms import RegisterForm
from flask.ext.security.registerable import register_user
from werkzeug.datastructures import MultiDict
from werkzeug.local import LocalProxy

from ..core import db
from ..helpers import current_wednesday, mail_content
from ..services import bundle, comics, roles, users


class UserBundlesCommand(Command):
    """
    Creates bundles for each user
    """
    def run(self):
        date = current_wednesday()
        issues_this_week = comics.issues.find_issue_with_date(date)
        for user in users.all():
            matches = [i for i in issues_this_week if i.title in user.pull_list and i.is_parent]
            # Get existing bundle if there already is one
            b = bundle.first(user=user, release_date=date)
            if b:
                b = bundle.update(b, issues=matches, last_updated=datetime.now())
            else:
                b = bundle.create(
                        user=user,
                        release_date=date,
                        issues=matches,
                        last_updated=datetime.now()
                )
        return


class MailBundlesCommand(Command):
    """
    Mails bundles to users
    """
    def run(self):
        date = current_wednesday()
        users_to_mail = users.find(mail_bundles=True)
        for user in users_to_mail:
            b = user.bundles.filter_by(release_date=date).first()
            if b.issues:
                html = render_template('mail/bundle_mail.html', issues=b.issues)
                mail_content(
                    [user.email],
                    'bundles@longboxed.com',
                    'Your weekly comic book bundle!',
                    'Content',
                    html
                )
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


class ListRolesCommand(Command):
    """List all roles"""

    def run(self):
        for r in roles.all():
            print 'Role(name=%s description=%s)' % (r.name, r.description)


class ListUsersCommand(Command):
    """List all users"""

    def run(self):
        for u in users.all():
            print 'User(id=%s email=%s)' % (u.id, u.email)