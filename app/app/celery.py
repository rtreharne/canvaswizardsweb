import os
from celery import Celery
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
app = Celery('app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

