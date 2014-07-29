# -*- coding: utf-8 -*-
"""
    longboxed.comics.forms
    ~~~~~~~~~~~~~~~~~~~~

    Comic forms
"""
from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired, ValidationError

from ..models import Title


def validate_title(form, field):
    if not Title.query.filter_by(name=field.data).first():
        raise ValidationError('Given title is not in Longboxed')

class AddToPullList(Form):
    title = TextField('Title', validators=[InputRequired(), validate_title])