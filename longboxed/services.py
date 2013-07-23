# -*- coding: utf-8 -*-
"""
    longboxed.services
    ~~~~~~~~~~~~~~~~~

    services module
"""

from .comics import ComicsService
from .users import UsersService

comics = ComicsService()

users = UsersService()