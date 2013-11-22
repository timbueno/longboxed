# -*- coding: utf-8 -*-
"""
    longboxed.comics.forms
    ~~~~~~~~~~~~~~~~~~~~

    Comic forms
"""
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import AnyOf, InputRequired, Length, Required


class AddToPullList(Form):
    # new_favorite = TextField('Title', validators=[Required()])
    title = TextField('Title', validators=[InputRequired()])