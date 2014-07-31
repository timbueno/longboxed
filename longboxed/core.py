# -*- coding: utf-8 -*-
"""
    longboxed.core
    ~~~~~~~~~~~~~~

    Core module contains basic classes that all applications
    depend on

    USE_AWS must be set as an environment variable.
    Values can be: 
        'True'   to use AWS for an image store
        'False'  for development / local image store
"""
import os

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security
from flask.ext.social import Social
from flask_mail import Mail

from .settings import config


#: Flask-SQLAlchemy extension instance
db = SQLAlchemy()

#: Flask-Security extension instance
security = Security()

#: Flask-Social exetension instance
social = Social()

#: Flask Mail Extension Instance
mail = Mail()

#: Image Filesystem
store = config[os.getenv('APP_ENV') or 'default'].get_store()


class LongboxedError(Exception):
    """Base application error class"""

    def __init__(self, msg):
        self.msg = msg

class LongboxedFormError(Exception):
    """Raise when an error processing a form occurs."""

    def __init__(self, errors=None):
        self.errors = errors


class CRUDMixin(object):
    """Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """

    @classmethod
    def _preprocess_params(cls, kwargs):
        """Returns a preprocessed dictionary of parameters. Used by default
        before creating a new instance or updating an existing instance.

        :param kwargs: a dictionary of parameters
        """
        for k in kwargs.keys():
            if not hasattr(cls, k):
                kwargs.pop(k, None)
        kwargs.pop('csrf_token', None)
        return kwargs

    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls.new(**kwargs)
        return instance.save()

    @classmethod
    def new(cls, **kwargs):
        """Create a new, unsaved record"""
        return cls(**cls._preprocess_params(kwargs))

    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in self._preprocess_params(kwargs).items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()