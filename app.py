import os
import psycopg2
from urllib.parse import urlparse
import logging
import time
from flask import Flask, render_template, request, jsonify
from celery import Celery
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# استخدام المتغيرات في الكود
DATABASE_URL = os.getenv('DATABASE_URL')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT', 5432)
DB_USER = os.getenv('DB_USER')

# تهيئة Flask
app = Flask(__name__)

# إعداد سجلات التتبع
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة Celery مع Redis كوسيط
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND')
celery = Celery(app.name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# إعداد الاتصال بقاعدة البيانات PostgreSQL مع محاولة إعادة الاتصال
def get_db_connection():
    attempts = 5
    while attempts > 0:
        try:
            if not DATABASE_URL:
                logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
                return None

            result = urlparse(DATABASE_URL)

            # تعديل الاتصال بقاعدة البيانات لتعطيل SSL
            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,  # استخدام اسم الخدمة الداخلية لـ PostgreSQL
                port=DB_PORT,
                sslmode='disable'  # تعطيل SSL
            )
            logger.info("تم الاتصال بقاعدة بيانات PostgreSQL بنجاح.")
            return conn
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            attempts -= 1
            if attempts == 0:
                logger.error("تم الوصول إلى الحد الأقصى من المحاولات، غير قادر على الاتصال بقاعدة البيانات.")
                return None
            logger.info(f"إعادة المحاولة... المحاولات المتبقية: {attempts}")
            time.sleep(5)

# دالة لإنشاء الجدول
def create_players_table():
    try:
        conn = get_db_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # إنشاء جدول اللاعبين
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS players (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                progress INT CHECK (progress >= 0 AND progress <= 100) NOT NULL
            );
        """)
        conn.commit()
        logger.info("تم إنشاء الجدول بنجاح.")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء الجدول: {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()

# تنفيذ الدالة لإنشاء الجدول عند بدء تشغيل التطبيق
create_players_table()

# مسار رئيسي لفتح التطبيق
@app.route('/')
def index():
    return render_template('index.html')

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
