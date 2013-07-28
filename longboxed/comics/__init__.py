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

    def find_relevent_comics_in_date_range(self, start, end, current_user):
        all_comics = self.find_comics_in_date_range(start, end)
        relevent_comics = all_comics
        matches = []
        if not current_user.is_anonymous():
            if current_user.settings.show_publishers:
                relevent_comics = [comic for comic in all_comics if comic.publisher in current_user.settings.show_publishers]
            if current_user.pull_list:
                if current_user.settings.display_pull_list:
                    matches = [c for c in all_comics if c.name in current_user.pull_list]
        return (relevent_comics, matches)

    def find_comic_with_diamondid(self, diamondid):
        try:
            return self.__model__.objects.get(diamondid=diamondid)
        except DoesNotExist:
            return None

    def distinct_publishers(self):
        try:
            return self.__model__.objects.distinct('publisher')
        except:
            return None

    def distinct_titles(self):
        try:
            return self.__model__.objects.distinct('name')
        except:
            return None   