from celery import Celery

def make_celery(app):
    # إنشاء كائن Celery مع إعدادات التطبيق
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],  # مكان تخزين النتائج
        broker=app.config['CELERY_BROKER_URL']  # مكان تخزين الرسائل (الـ Queue)
    )

    # تحديث إعدادات Celery باستخدام إعدادات Flask
    celery.conf.update(app.config)

    # إرجاع كائن Celery المعدل
    return celery
