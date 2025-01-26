from celery import Celery
from app import app  # استيراد تطبيق Flask من app.py

# تهيئة Celery
celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)
celery.conf.update(app.config)

if __name__ == '__main__':
    celery.start()
