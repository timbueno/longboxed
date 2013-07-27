# -*- coding: utf-8 -*-
"""
    longboxed.comics
    ~~~~~~~~~~~~~~

    longboxed comics package
"""
from mongoengine.queryset import DoesNotExist

from ..core import Service
from .models import Comic

class ComicsService(Service):
    __model__ = Comic

    def find_comics_in_date_range(self, start, end):
        return sorted(self.__model__.objects(onSaleDate__gte=start, onSaleDate__lte=end))

    def find_comic_with_diamondid(self, diamondid):
        try:
            return self.__model__.objects.get(diamondid=diamondid)
        except DoesNotExist:
            return None