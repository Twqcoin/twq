import os
import psycopg2
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from celery import Celery

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# إعداد تسجيل الأخطاء (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إعداد Flask
app = Flask(__name__)

# إعداد Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# إعداد Celery Broker (نحتاج لإعداد RabbitMQ أو Redis كوسيط)
app.config.update(
    CELERY_BROKER_URL=os.getenv('CELERY_BROKER_URL', ''),
    CELERY_RESULT_BACKEND=os.getenv('CELERY_RESULT_BACKEND', '')
)

celery = make_celery(app)

# دالة لإنشاء الجدول في قاعدة البيانات
def create_table_in_db():
    try:
        # التحقق من وجود جميع المتغيرات البيئية المطلوبة
        required_env_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        for var in required_env_vars:
            if not os.getenv(var):
                raise ValueError(f"المتغير البيئي المطلوب غير موجود: {var}")

        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')  # المنفذ الافتراضي لـ PostgreSQL
        )

        # استخدام with لإدارة الاتصال والكورسور
        with conn:
            with conn.cursor() as cursor:
                # إنشاء الجدول إذا لم يكن موجودًا
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS players (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        image_url TEXT NOT NULL
                    );
                """)
                logger.info("تم إنشاء الجدول بنجاح!")

    except Exception as e:
        logger.error(f"حدث خطأ: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات.")

# دالة Celery لإنشاء الجدول في الخلفية
@celery.task(bind=True)
def create_table_async(self):
    create_table_in_db()

# إعداد نقطة النهاية في Flask لاستقبال الطلبات
@app.route('/create_table', methods=['POST'])
def create_table():
    try:
        create_table_async.apply_async()  # تشغيل المهمة في الخلفية
        return jsonify({"message": "تم بدء مهمة إنشاء الجدول!"}), 202
    except Exception as e:
        logger.error(f"حدث خطأ: {e}")
        return jsonify({"error": str(e)}), 500

# تشغيل تطبيق Flask
if __name__ == '__main__':
    app.run(debug=True)