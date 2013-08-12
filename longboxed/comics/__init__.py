# -*- coding: utf-8 -*-
"""
    longboxed.comics
    ~~~~~~~~~~~~~~

    longboxed comics package
"""
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
        titles = sorted(self.__model__.query.filter(self.__model__.on_sale_date.between(s,e)))
        sorted_titles = sorted(titles, key=lambda k: k.publisher.name)
        return sorted_titles

    def find_relevent_issues_in_date_range(self, start, end, current_user):
        all_issues = self.find_issues_in_date_range(start, end)
        relevent_issues = all_issues
        matches = []
        if not current_user.is_anonymous():
            if current_user.publishers:
                relevent_issues = [issue for issue in all_issues if issue.publisher in current_user.publishers]
            if current_user.pull_list:
                if current_user.display_pull_list:
                    matches = [c for c in all_issues if c.title in current_user.pull_list]
        return (relevent_issues, matches)

    def distinct_publishers(self):
        try:
            return self.__model__.objects.distinct('publisher')
        except:
            return None


class ComicService(object):
    def __init__(self):
        self.publishers = PublisherService()
        self.titles = TitleService()
        self.issues = IssueService()

    def insert_comic(self, p=None, t=None, i=None):
        publisher = self.publishers.first(name=p['name'])
        if not publisher:
            print 'Adding Publisher: %s' % p['name']
            publisher = self.publishers.new(**p)
            self.publishers.save(publisher)

        title = self.titles.first(name=t['name'])
        if not title:
            print 'Adding Title: %s' % t['name']
            t['publisher'] = publisher
            title = self.titles.new(**t)
            self.titles.save(title)

        issue = self.issues.first(product_id=i['diamond_id'])
        if not issue:
            print 'Adding Issue: %s' % i['diamond_id']
            i['publisher'] = publisher
            i['title'] = title
            issue = self.issues.new(**i)
            self.issues.save(issue)
            
        return










