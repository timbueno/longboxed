# -*- coding: utf-8 -*-
"""
    longboxed.users.forms
    ~~~~~~~~~~~~~~~~~~~~

    User forms
"""
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import DataRequired, InputRequired

class UserInformationForm(Form):
    first_name = TextField('First Name', validators=[InputRequired()])
    last_name = TextField('Last Name', validators=[InputRequired()])

class DeleteUserAccountForm(Form):
    delete_confirmation = BooleanField('I understand.', validators=[DataRequired()])

