import os
from celery import Celery

# Set the default settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'passenger_api.settings')

app = Celery('passenger_api')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks in all installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
