# -*- coding: utf-8 -*-
"""
    longboxed.users
    ~~~~~~~~~~~~~~

    longboxed users package
"""
from mongoengine.queryset import DoesNotExist
# from flask.ext.mongoengine.wtf import model_form

from ..core import Service
from .models import User

class UsersService(Service):
    __model__ = User

    def new(self):
        return self.__model__()

    def find_user_with_id(self, userid):
        try:
            return self.__model__.objects.get(userid=userid)
        except DoesNotExist:
            print 'USER DOES NOT EXIST'
            return None