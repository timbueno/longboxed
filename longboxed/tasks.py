# -*- coding: utf-8 -*-
"""
    overholt.tasks
    ~~~~~~~~~~~~~~

    overholt tasks module
"""
from .factory import create_celery_app
from .services import comics

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


@celery.task(name='tasks.diamondtest')
def cross_check():
    content = comics.get_shipping_this_week()
    shipping = comics.get_diamond_ids_shipping(content)
    # for item in shipping:
    #     print item
    # print len(shipping)
    comics.compare_shipping_with_database(shipping)
