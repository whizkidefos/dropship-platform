from celery import Celery
from flask import current_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Create the celery app without Flask context
celery = Celery(
    'app',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task
def test_task():
    return "Celery is working!"


@celery.task
def process_order(order_id):
    """Process a new order"""
    with app.app_context():
        order = Order.query.get(order_id)
        if not order:
            return
        
        try:
            # Update order status
            order.status = 'processing'
            
            # Create log entry
            log = OrderLog(
                order_id=order.id,
                status='processing',
                notes='Order processing started'
            )
            db.session.add(log)
            
            # Perform processing tasks here
            # - Update inventory
            # - Send notifications
            # - Contact supplier
            
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            raise


@celery.task
def send_order_notification(order_id, notification_type):
    """Send order-related notifications"""
    with app.app_context():
        order = Order.query.get(order_id)
        if not order:
            return
            
        if notification_type == 'status_update':
            # Send status update email
            pass
        elif notification_type == 'shipping_confirmation':
            # Send shipping confirmation
            pass