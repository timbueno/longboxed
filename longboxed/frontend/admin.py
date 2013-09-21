# -*- coding: utf-8 -*-
"""
    longboxed.frontend.assets
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    frontend application asset "pipeline"
"""
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView

from ..core import db
from ..models import Issue, Publisher, Title, User


class IssueAdmin(ModelView):
    # List of columns that can be sorted
    column_sortable_list = ('issue_number', 'complete_title', 'on_sale_date', ('title',Title.name), ('publisher', Publisher.name))
    # column_searchable_list = ('title')
    column_list = ('on_sale_date', 'issue_number', 'issues', 'complete_title', 'title', 'publisher')
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(IssueAdmin, self).__init__(Issue, session)


class PublisherAdmin(ModelView):
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(PublisherAdmin, self).__init__(Publisher, session) 


class TitleAdmin(ModelView):
    column_sortable_list= ('name', ('publisher', Publisher.name))
    # column_searchable_list = ('name')
    def __init__(self, session):
        # Just call parent class with predefined model.
        super(TitleAdmin, self).__init__(Title, session)        


class UserAdmin(ModelView):
    column_list = ('email', 'last_login_at', 'login_count', 'pull_list')

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(UserAdmin, self).__init__(User, session)


def init_app(app):
    admin = Admin(app)
    admin.add_view(UserAdmin(db.session))
    admin.add_view(IssueAdmin(db.session))
    admin.add_view(PublisherAdmin(db.session))
    admin.add_view(TitleAdmin(db.session))