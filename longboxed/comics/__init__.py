# -*- coding: utf-8 -*-
"""
    longboxed.comics
    ~~~~~~~~~~~~~~~~

    longboxed comics package
"""
from logging import getLogger
from re import split

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy_imageattach.entity import store_context
from requests import get

from ..core import store, Service
from .models import Bundle, Creator, Issue, Publisher, Title


process_logger = getLogger('issue_processing')


class BundleService(Service):
    __model__ = Bundle


class PublisherService(Service):
    __model__ = Publisher


class TitleService(Service):
    __model__ = Title


class CreatorService(Service):
    __model__ = Creator


class IssueService(Service):
    __model__ = Issue

    def set_cover_image_from_url(self, issue, url, overwrite=False, default=False):
        """
        Downloads a jpeg file from a url and stores it in the image store.

        :param issue: :class:`Issue` object class
        :param url: URL to download the jpeg cover image format
        :param overwrite: Boolean flag that overwrites an existing image
        """
        created_flag = False
        if not issue.cover_image.original or overwrite:
            r = get(url)
            if r.status_code == 200 and r.headers['content-type'] == 'image/jpeg':
                with store_context(store):
                    issue.cover_image.from_blob(r.content)
                    issue = self.save(issue)
                    issue.cover_image.generate_thumbnail(height=600)
                    issue = self.save(issue)
                    created_flag = True
        return created_flag

    def find_or_create_thumbnail(self, issue, width=None, height=None):
        """
        Creates a thumbnail image from the original if one of the same size
        does not already exist. Width OR height must be provided. It is not
        necessary to provide both.

        Default Image (We should act on this in the future)
        http://affimg.tfaw.com/covers_tfaw/400/no/nocover.jpg

        :param issue: :class:`Issue` object class
        :param width: Width of desired thumbnail image
        :param height: Height of desired thumbnail image
        """
        assert width is not None or height is not None
        with store_context(store):
            try:
                image = issue.cover_image.find_thumbnail(width=width, height=height)
            except NoResultFound:
                image = issue.cover_image.generate_thumbnail(width=width, height=height)
            issue = self.save(issue)
        return image

    def find_issues_in_date_range(self, start, end):
        """
        Depricated

        Finds issues in the given date range

        :param start: :class:`Date` class to start the search on
        :param end: :class:`Date` class to end the search on
        """

        titles = sorted(self.__model__.query.filter(self.__model__.on_sale_date.between(start,end)))
        sorted_titles = sorted(titles, key=lambda k: k.publisher.name)
        return sorted_titles

    def find_relevent_issues_in_date_range(self, start, end, current_user):
        """
        Depricated

        Gets issue objects in a date range only if their publisher attribute
        matches the users choices. Also returns another value, matches, which
        are titles being released also on the users pull list

        :param start: :class:`Date` class to start the search on
        :param end: :class:`Date` class to end the search on
        :param current_user: :class:`User` class used to extract their pull list
        """
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

    def find_issue_with_date(self, date):
        """
        Gets all issue objects whose on_sale_date attribute matches 
        the given date.

        :param date: :class:`Date` object you wish to pull issues from
        """
        titles = sorted(self.__model__.query.filter(self.__model__.on_sale_date == date))
        return sorted(titles, key=lambda k: k.publisher.name)


class ComicService(object):
    """
    The ComicService class is not an actual service class. However, it wraps
    three service classes for convenience purposes. The publsishers, titles, 
    and issues classes are all available from ComicService. 

    Processes like adding an issue to the database require manipulating Issue,
    Title, and Publisher objects. ComicService gives access to functions that 
    need to manipulate all three of these objects at the same time.
    """

    def __init__(self):
        self.publishers = PublisherService()
        self.titles = TitleService()
        self.issues = IssueService()
        self.creators = CreatorService()

    def insert_publisher(self, raw_publisher=None):
        """
        Inserts a publisher into the database if it does not already
        exist. 

        :param raw_publisher: String containing publisher name
        """
        publisher = self.publishers.first(name=raw_publisher)
        if not publisher:
            publisher = self.publishers.create(name=raw_publisher)
            process_logger.info('PUBLISHER: %s' % (publisher.name))
        return publisher

    def insert_title(self, raw_title, publisher_object):
        """
        Inserts a title into the database if it does not already
        exist. 

        :param raw_title: String containing title name
        :param publisher_object: Publisher model instance to link the title to
        """
        title = self.titles.first(name=raw_title)
        if not title:
            title = self.titles.create(name=raw_title, publisher=publisher_object)
            process_logger.info('TITLE: %s' % (title.name))
        return title

    def insert_creators(self, raw_creators):
        """
        Inserts creators into the database if they do not already exist.
        """
        creator_list = []
        people = split(';|,', raw_creators)
        for person in people:
            person = person.strip()
            creator = self.creators.first(name=person)
            if not creator:
                creator = self.creators.create(name=person)
                process_logger.info('CREATOR: %s' % (creator.name))
            creator_list.append(creator)
        return creator_list


    def insert_issue(self, raw_issue_dict, title_object, publisher_object, creator_objects):
        """
        Inserts an issue into the database if it does not already
        exist. 

        :param raw_issue_dict: Dictionary conatining issue data from TFAW
        :param publisher_object: Publisher model instance to link the issue to
        :param title_object: Title model instance to link the issue to
        """
        issue = self.issues.first(diamond_id=raw_issue_dict['diamond_id'])
        raw_issue_dict['title'] = title_object
        raw_issue_dict['publisher'] = publisher_object
        raw_issue_dict['creators'] = creator_objects
        if issue:
            issue = self.issues.update(issue, **raw_issue_dict) # Update
        else:
            issue = self.issues.create(**raw_issue_dict) # Create
            process_logger.info('ISSUE: %s ID: %s' % (issue.complete_title, issue.diamond_id))
        return issue
