# -*- coding: utf-8 -*-
"""
    longboxed.services
    ~~~~~~~~~~~~~~~~~

    services module
"""

from .comics import ComicService, BundleService
from .users import UsersService, RolesService


bundle = BundleService()
comics = ComicService()

users = UsersService()

roles = RolesService()