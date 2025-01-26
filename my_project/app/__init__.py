from flask import Flask
from celery import Celery
from config import Config

# إنشاء تطبيق Flask
app = Flask(__name__)
app.config.from_object(Config)

# إعداد Celery
celery = Celery(
    app.import_name,
    backend=app.config['CELERY_RESULT_BACKEND'],
    broker=app.config['CELERY_BROKER_URL']
)
celery.conf.update(app.config)

# استيراد نقاط النهاية والمهام
from app import routes, tasks