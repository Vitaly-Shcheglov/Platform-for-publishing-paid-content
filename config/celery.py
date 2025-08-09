import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("Django_LMS_project")

app.conf.timezone = "UTC"

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "notify-users-about-upcoming-courses-every-hour": {
        "task": "courses.tasks.notify_users_about_upcoming_courses",
        "schedule": 3600.0,
    },
    "deactivate-inactive-users-every-day": {
        "task": "users.tasks.deactivate_inactive_users",
        "schedule": crontab(hour=0, minute=0),
    },
}
