from flask import Flask, render_template, request, jsonify
from celery import Celery
import os
import requests
import psycopg2
from urllib.parse import urlparse
import logging
import certifi
from dotenv import load_dotenv
import time

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# تهيئة Flask
app = Flask(__name__)

# إعداد سجلات التتبع
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة Celery مع Redis كوسيط
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# إنشاء Celery
celery = make_celery(app)

# إعداد الاتصال بقاعدة البيانات PostgreSQL مع محاولة إعادة الاتصال
def get_db_connection():
    attempts = 5
    while attempts > 0:
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
                return None

            result = urlparse(database_url)
            db_port = os.getenv("DB_PORT", 5432)

            conn = psycopg2.connect(
                database=result.path[1:],
                user=result.username,
                password=result.password,
                host="postgres",  # استخدام اسم الخدمة الداخلية لـ PostgreSQL
                port=db_port,
                sslmode='require',
                sslrootcert=certifi.where()
            )
            logger.info("Connected to PostgreSQL database successfully.")
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            attempts -= 1
            if attempts == 0:
                logger.error("Max attempts reached, unable to connect to database.")
                return None
            logger.info(f"Retrying... attempts left: {attempts}")
            time.sleep(5)  # الانتظار قبل إعادة المحاولة

# باقي الكود كما هو
# ...

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
