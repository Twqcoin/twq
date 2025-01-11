import os
from celery import Celery
from flask import Flask

app = Flask(__name__)

# استخدام المتغير البيئي CELERY_BROKER_URL
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # القيمة الافتراضية إذا لم يتم تعيين المتغير

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
