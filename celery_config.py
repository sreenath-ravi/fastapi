from celery import Celery
from celery.schedules import crontab

celery_app = Celery(
    'tasks',
    broker='pyamqp://guest@localhost//',  # RabbitMQ broker
    backend='redis://localhost'    # Redis backend
)



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
