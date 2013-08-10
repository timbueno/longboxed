# -*- coding: utf-8 -*-
"""
    longboxed.comics
    ~~~~~~~~~~~~~~

    longboxed comics package
"""
# from mongoengine.queryset import DoesNotExist

from ..core import Service
from .models import Issue, Publisher, Title


class PublisherService(Service):
    __model__ = Publisher


class TitleService(Service):
    __model__ = Title


class IssueService(Service):
    __model__ = Issue

    def find_issues_in_date_range(self, start, end):
        s = start.strftime('%Y-%m-%d')
        e = end.strftime('%Y-%m-%d')
        return sorted(self.__model__.query.filter(self.__model__.on_sale_date.between(s,e)))
    
    def find_relevent_issues_in_date_range(self, start, end, current_user):
        all_issues = self.find_issues_in_date_range(start, end)
        relevent_issues = all_issues
        matches = []
        if not current_user.is_anonymous():
            if current_user.publishers:
                relevent_issues = [issue for issue in all_issues if issue.publisher in current_user.show_publishers]
            if current_user.pull_list:
                if current_user.display_pull_list:
                    matches = [c for c in all_issues if c.name in current_user.pull_list]
        return (relevent_issues, matches)

    def find_issue_with_diamondid(self, diamondid):
        try:
            return self.__model__.objects.get(diamondid=diamondid)
        except DoesNotExist:
            return None

    def distinct_publishers(self):
        try:
            return self.__model__.objects.distinct('publisher')
        except:
            return None


class ComicService(object):
    publishers = PublisherService()
    titles = TitleService()
    issues = IssueService()

    def insert_comic(self, publisher, title, issue):
        p = self.publishers.get(name=publisher.name)
        if not p:
            self.publishers.save(publisher)
        t = self.titles.get(name=title.name)
        if not t:
            self.titles.save(title)
        i = self.issues.get(product_id=issue.product_id)
        if not i:
            self.issues.save(issue)
        return










