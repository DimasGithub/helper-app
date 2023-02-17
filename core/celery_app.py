# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
URL_BROKER=f"amqp://{settings.BROKER_USERNAME}:{settings.BROKER_PASSWORD}@{settings.BROKER_HOST}/{settings.BROKER_VHOST}"
app = Celery('core', broker=URL_BROKER)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
