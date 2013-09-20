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
    # column_sortable_list = ('issue_number', 'complete_title', ('publisher', Publisher.name))
    column_list = ('issue_number', 'issues', 'complete_title', 'title', 'publisher')

    form_ajax_refs = {
        'publisher': ('name',)
    }

    def __init__(self, session):
        # Just call parent class with predefined model.
        super(IssueAdmin, self).__init__(Issue, session)

def init_app(app):
    admin = Admin(app)
    admin.add_view(ModelView(User, db.session))
    # admin.add_view(ModelView(Issue, db.session))
    admin.add_view(IssueAdmin(db.session))
    admin.add_view(ModelView(Publisher, db.session))
    admin.add_view(ModelView(Title, db.session))