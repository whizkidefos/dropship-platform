from flask import current_app
from celery import Celery

celery = Celery('app')

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

@celery.task
def test_task():
    return "Celery is working!"