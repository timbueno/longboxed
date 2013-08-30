# -*- coding: utf-8 -*-
"""
    overholt.tasks
    ~~~~~~~~~~~~~~

    overholt tasks module
"""
from .factory import create_celery_app
from .save_from_tfaw import add_comics_to_db
from .services import comics

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


@celery.task(name='tasks.test')
def test():
    print 'firing test task'


@celery.task(name='tasks.addissues')
def get_new_issues():
    comics.test_grouping()
