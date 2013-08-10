# -*- coding: utf-8 -*-
"""
    longboxed.services
    ~~~~~~~~~~~~~~~~~

    services module
"""

from .comics import ComicService
from .users import UsersService

comics = ComicService()

users = UsersService()