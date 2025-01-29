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

# استخدام المتغيرات في الكود
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_USER = os.getenv('DB_USER')
FLASK_APP = os.getenv('FLASK_APP')

# تهيئة Flask
app = Flask(__name__)

# إعداد سجلات التتبع
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تأكد من أن المتغيرات البيئية تم تحميلها بشكل صحيح
logger.info(f"Celery Broker URL: {CELERY_BROKER_URL}")
logger.info(f"Celery Result Backend: {CELERY_RESULT_BACKEND}")
logger.info(f"Database URL: {DATABASE_URL}")

# تهيئة Celery مع Redis كوسيط باستخدام المتغيرات البيئية
app.config['CELERY_BROKER_URL'] = CELERY_BROKER_URL
app.config['CELERY_RESULT_BACKEND'] = CELERY_RESULT_BACKEND

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
            if not DATABASE_URL:
                logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
                return None

            result = urlparse(DATABASE_URL)

            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,  # استخدام اسم الخدمة الداخلية لـ PostgreSQL
                port=DB_PORT,
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

# مسار رئيسي للتحقق من أن التطبيق يعمل بشكل صحيح
@app.route('/')
def index():
    return 'App is live at https://twq-xzy4.onrender.com'

# إضافة مهمة Celery بسيطة
@celery.task
def add_numbers(a, b):
    return a + b

@app.route('/add')
def add():
    result = add_numbers.apply_async((5, 7))  # حساب 5 + 7 باستخدام Celery
    return jsonify(result=result.get(timeout=10))  # الحصول على النتيجة

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
