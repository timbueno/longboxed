# -*- coding: utf-8 -*-
"""
    longboxed.users
    ~~~~~~~~~~~~~~

    longboxed users package
"""

from ..core import Service
from .models import User

class UsersService(Service):
    __model__ = User