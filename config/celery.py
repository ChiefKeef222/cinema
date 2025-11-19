import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

# autodiscover_tasks will now look for tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
