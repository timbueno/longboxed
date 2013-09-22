# -*- coding: utf-8 -*-
"""
    longboxed.frontend.assets
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    frontend application asset "pipeline"
"""
from flask import flash
from flask.ext.security import current_user
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.actions import action
from flask.ext.admin.babel import gettext, lazy_gettext
from flask.ext.admin.contrib.sqlamodel import ModelView

from ..core import db
from ..helpers import current_wednesday, last_wednesday, next_wednesday 
from ..services import comics as _comics
from ..models import Issue, Publisher, Title, User, Role


class LongboxedAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

class AdministratorBase(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

class SuperUserBase(ModelView):
    def is_accessible(self):
        return (current_user.has_role('admin') and
                current_user.has_role('super'))


class IssueAdmin(AdministratorBase):
    # List of columns that can be sorted
    column_sortable_list = ('issue_number', 'complete_title', 'on_sale_date', ('title',Title.name), ('publisher', Publisher.name))
    column_searchable_list = ('complete_title', 'diamond_id')
    column_list = ('on_sale_date', 'diamond_id', 'issue_number', 'issues', 'complete_title', 'title', 'publisher')
    
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(IssueAdmin, self).__init__(Issue, session)

    def set_on_sale_date(self, ids, date):
        try:
            issues = _comics.issues.get_all(*ids)
            for issue in issues:
                _comics.issues.update(issue, **{'on_sale_date': date})
        except Exception, ex:
            flash(gettext('Failed to set date %(error)s', error=str(ex)), 'error')

    @action('current_wednesday', lazy_gettext('This Wed | %(date)s', date=current_wednesday()), lazy_gettext('Are you sure? | %(date)s', date=current_wednesday()))
    def action_current_wednesday(self, ids):
        self.set_on_sale_date(ids, current_wednesday())

    @action('next_wednesday', lazy_gettext('Next Wed | %(date)s', date=next_wednesday()), lazy_gettext('Are you sure? | %(date)s', date=next_wednesday()))
    def action_next_wednesday(self, ids):
        self.set_on_sale_date(ids, next_wednesday())

    @action('last_wednesday', lazy_gettext('Last Wed | %(date)s', date=last_wednesday()), lazy_gettext('Are you sure? | %(date)s', date=last_wednesday()))
    def action_last_wednesday(self, ids):
        self.set_on_sale_date(ids, last_wednesday())

    @action('no_date', lazy_gettext('No Date'), lazy_gettext('Are you sure? | No Date'))
    def action_no_date(self, ids):
        self.set_on_sale_date(ids, None)

class PublisherAdmin(AdministratorBase):
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(PublisherAdmin, self).__init__(Publisher, session) 


class TitleAdmin(AdministratorBase):
    column_sortable_list= ('name', ('publisher', Publisher.name))
    # column_searchable_list = ('name')
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(TitleAdmin, self).__init__(Title, session)        


class UserAdmin(SuperUserBase):
    column_list = ('email', 'last_login_at', 'login_count', 'pull_list', 'roles')
    column_searchable_list = ('email',)

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(UserAdmin, self).__init__(User, session)


class RoleAdmin(SuperUserBase):
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(RoleAdmin, self).__init__(Role, session)


def init_app(app):
    admin = Admin(app, index_view=LongboxedAdminIndexView())
    admin.add_view(UserAdmin(db.session))
    admin.add_view(IssueAdmin(db.session))
    admin.add_view(PublisherAdmin(db.session))
    admin.add_view(TitleAdmin(db.session))
    admin.add_view(RoleAdmin(db.session))