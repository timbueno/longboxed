# -*- coding: utf-8 -*-
"""
    longboxed.services
    ~~~~~~~~~~~~~~~~~

    services module
"""

from .comics import ComicService
from .users import UsersService, RolesService


comics = ComicService()

users = UsersService()

roles = RolesService()