# -*- coding: utf-8 -*-
"""
    longboxed.comics.forms
    ~~~~~~~~~~~~~~~~~~~~

    Comic forms
"""
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired, ValidationError

from ..services import comics as _comics


def validate_title(form, field):
    if not _comics.titles.first(name=field.data):
        raise ValidationError('Given title is not in Longboxed')

class AddToPullList(Form):
    # new_favorite = TextField('Title', validators=[Required()])
    title = TextField('Title', validators=[InputRequired(), validate_title])