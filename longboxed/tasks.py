# -*- coding: utf-8 -*-
"""
    overholt.tasks
    ~~~~~~~~~~~~~~

    overholt tasks module
"""
from .factory import create_celery_app

celery = create_celery_app()

@celery.task
def add(x,y):
    return x+y

@celery.task(name='tasks.test')
def test():
    print 'firing test task'
