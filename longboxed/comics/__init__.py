# -*- coding: utf-8 -*-
"""
    longboxed.comics
    ~~~~~~~~~~~~~~

    longboxed comics package
"""

from ..core import Service
from .models import Comic

class ComicsService(Service):
    __model__ = Comic

    def find_comics_in_date_range(self, start, end):
        return sorted(self.__model__.objects(onSaleDate__gte=start, onSaleDate__lte=end))


# def find_comics_in_date_range(start, end):
#     result = list(collection.comics.Comic.find({"onSaleDate": {"$gte": start, "$lt": end}}))
#     result = sorted(result, key=lambda k: k.publisher)
#     return result

# def find_relevent_comics_in_date_range(start, end):
#     allComics = find_comics_in_date_range(start, end)
#     releventComics = allComics
#     matches = []
#     if not current_user.is_anonymous():
#         if current_user.settings.publishers:
#             releventComics = [comic for comic in allComics if comic.publisher in current_user.settings.publishers]
#         if current_user.comics.favorites:
#             matches = get_favorite_matches(current_user.comics.favorites, allComics)
#     return (releventComics, matches)