"""
Celery configuration for xmen_agileteam project.
"""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xmen_agileteam.settings')

app = Celery('xmen_agileteam')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    'daily-deadline-alerts': {
        'task': 'apps.notifications.tasks.daily_deadline_alerts',
        'schedule': 60.0 * 60 * 24,  # Daily at midnight
    },
    'recalc-project-metrics': {
        'task': 'apps.dashboards.tasks.recalc_project_metrics',
        'schedule': 60.0 * 60,  # Every hour
    },
    'generate-recommendations': {
        'task': 'apps.recommendations.tasks.generate_recommendations',
        'schedule': 60.0 * 60 * 6,  # Every 6 hours
    },
}