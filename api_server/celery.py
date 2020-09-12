import os
from celery import Celery
import kombu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_server.settings')

app = Celery('api_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


with app.pool.acquire(block=True) as conn:
    train_exchange = kombu.Exchange(
        name='ems_train_exchange',
        type='direct',
        durable=True,
        channel=conn,
    )
    train_exchange.declare()

    queue = kombu.Queue(
        name = 'ems_train_queue',
        exchange=train_exchange,
        routing_key='train',
        channel=conn,
        message_ttl=600,
        queue_arguments={
            'x-queue-type':'classic'
        },
        durable=True
    )
    queue.declare()
