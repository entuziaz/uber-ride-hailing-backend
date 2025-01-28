from __future__ import absolute_import, unicode_literals

# Ensure Celery app always imported when Django starts
# so that shared tasks use this app.
from .celery import app as celery_app

__all__ = ('celery_app',)
