# -*- coding: utf-8 -*-
"""
    overholt.tasks
    ~~~~~~~~~~~~~~

    overholt tasks module
"""

# from .core import mail
from .factory import create_celery_app
from .save_from_tfaw import add_comics_to_db

celery = create_celery_app()


@celery.task(name='tasks.addcomics')
def get_new_comics():
    add_comics_to_db()

@celery.task
def talk():
    print 'Hey whats going on man?'


@celery.task
def add(x,y):
    return x+y

# @celery.task
# def send_manager_added_email(*recipients):
#     print 'sending manager added email...'


# @celery.task
# def send_manager_removed_email(*recipients):
#     print 'sending manager removed email...'
