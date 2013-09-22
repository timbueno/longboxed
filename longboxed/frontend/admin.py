# -*- coding: utf-8 -*-
"""
    longboxed.frontend.assets
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    frontend application asset "pipeline"
"""
from flask.ext.security import current_user
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqlamodel import ModelView

from ..core import db
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
    # column_searchable_list = ('title')
    column_list = ('on_sale_date', 'issue_number', 'issues', 'complete_title', 'title', 'publisher')
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(IssueAdmin, self).__init__(Issue, session)


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

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(UserAdmin, self).__init__(User, session)


class RoleAdmin(ModelView):
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