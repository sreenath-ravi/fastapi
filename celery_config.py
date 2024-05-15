from celery import Celery, Task
from celery.schedules import crontab

def make_celery(app_name=__name__):
    return Celery(
        app_name,
        broker='pyamqp://guest@localhost//',  # RabbitMQ broker
        backend='redis://localhost:6379/0',          # Redis backend
        include=['tasks']                     # Include tasks module
    )

celery_app = make_celery()


celery_app.conf.update(
    result_expires=3600,
    beat_schedule={
        'fetch-store-data-every-minute': {
            'task': 'fetch_store_data_task',
            'schedule': crontab(minute='*'),
            'args': ('in',)  # Default argument for the task
        },
    }
)
