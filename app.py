import os
import psycopg2
from urllib.parse import urlparse
import logging
import time
from flask import Flask, request, jsonify
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

# إعداد الاتصال بقاعدة البيانات PostgreSQL بدون شهادات SSL
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
                port=DB_PORT
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
def create_wallets_table():
    try:
        conn = get_db_connection()
        if conn is None:
            return

        cursor = conn.cursor()

        # إنشاء جدول المحفظات
        cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS wallets (
                id SERIAL PRIMARY KEY,
                address VARCHAR(255) UNIQUE NOT NULL
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
create_wallets_table()

# نقطة لحفظ عنوان المحفظة
@app.route('/save-wallet-address', methods=['POST'])
def save_wallet_address():
    wallet_address = request.form.get('wallet_address')

    if not wallet_address:
        return jsonify(message="عنوان المحفظة مفقود"), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify(message="فشل الاتصال بقاعدة البيانات."), 500

        cursor = conn.cursor()

        # تخزين عنوان المحفظة في قاعدة البيانات
        cursor.execute("""
            INSERT INTO wallets (address) 
            VALUES (%s)
        """, (wallet_address,))

        conn.commit()
        logger.info(f"تم حفظ عنوان المحفظة: {wallet_address}")

        return jsonify(message="تم حفظ عنوان المحفظة بنجاح")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء حفظ عنوان المحفظة: {e}")
        return jsonify(message="فشل في حفظ عنوان المحفظة"), 500
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
