# -*- coding: utf-8 -*-
"""
    longboxed.comics.forms
    ~~~~~~~~~~~~~~~~~~~~~~~

    Comic forms
"""

from ..core import Service
from .models import Comic

class ComicsService(Service):
    __model__ = Comic