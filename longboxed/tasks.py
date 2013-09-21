# -*- coding: utf-8 -*-
"""
    overholt.tasks
    ~~~~~~~~~~~~~~

    overholt tasks module
"""
from .factory import create_celery_app
from .services import comics, roles

celery = create_celery_app()

@celery.task
def talk():
    print 'Hey whats going on man?'


@celery.task
def add(x,y):
    return x+y


@celery.task(name='tasks.test')
def test():
    print 'firing test task'

@celery.task(name='tasks.addissues')
def add_new_issues_to_database():
    comics.add_new_issues_to_database()


@celery.task(name='tasks.cross_check')
def cross_check():
    content = comics.get_shipping_this_week()
    shipping = comics.get_diamond_ids_shipping(content)
    comics.compare_shipping_with_database(shipping)


@celery.task(name='tasks.add_and_check')
def add_and_check():
    add_new_issues_to_database()
    cross_check()
