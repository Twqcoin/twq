from celery import Celery

# تأجيل استيراد Flask بعد تهيئة التطبيق
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# لا نقوم بإنشاء celery هنا
# سيتم إنشاؤه بعد تهيئة التطبيق
