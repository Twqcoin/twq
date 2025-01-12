from celery import Celery

def make_celery(app):
    # تهيئة كائن Celery
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    # تحديث إعدادات Celery باستخدام إعدادات Flask
    celery.conf.update(app.config)
    
    return celery
