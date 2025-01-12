from celery import Celery

def make_celery(app):
    # إعداد Celery مع Flask
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)  # تطبيق إعدادات Flask على Celery
    return celery
