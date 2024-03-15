import os
from celery import Celery

# import settings
from django.conf import settings

os.environ.setdefault(settings, 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

