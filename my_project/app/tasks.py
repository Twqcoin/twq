from app import celery
import psycopg2
import os
import logging

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def create_table_async(self):
    try:
        # الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=os.getenv('DB_PORT', '5432')
        )

        # إنشاء الجدول
        with conn:
            with conn.cursor() as cursor:
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