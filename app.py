import os
import psycopg2
from urllib.parse import urlparse
import logging
import time
from flask import Flask, render_template, request, jsonify
import requests
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

# طباعة المتغيرات البيئية (للتأكد من تحميلها بشكل صحيح)
logger = logging.getLogger(__name__)
logger.info(f"DATABASE_URL: {DATABASE_URL}")
logger.info(f"DB_HOST: {DB_HOST}")
logger.info(f"DB_USER: {DB_USER}")

# تهيئة Flask
app = Flask(__name__)

# إعداد سجلات التتبع
logging.basicConfig(level=logging.INFO)

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

            # تعديل الاتصال بقاعدة البيانات لتمكين SSL
            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,  # استخدام اسم الخدمة الداخلية لـ PostgreSQL
                port=DB_PORT,
                sslmode='require',  # تمكين SSL
                sslrootcert='/path/to/ca-cert.pem',  # المسار إلى شهادة الجذر (إذا لزم الأمر)
                sslcert='/path/to/client-cert.pem',  # المسار إلى شهادة العميل (إذا لزم الأمر)
                sslkey='/path/to/client-key.pem'  # المسار إلى مفتاح العميل (إذا لزم الأمر)
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

# نقطة نهاية لاختبار الاتصال بقاعدة البيانات
@app.route('/test-db-connection')
def test_db_connection():
    conn = get_db_connection()
    if conn:
        return "تم الاتصال بقاعدة البيانات بنجاح!"
    else:
        return "فشل الاتصال بقاعدة البيانات."

# نقطة نهاية لحفظ بيانات اللاعب
@app.route('/save-player', methods=['POST'])
def save_player():
    player_name = request.form['name']
    player_progress = int(request.form['progress'])

    try:
        conn = get_db_connection()
        if conn is None:
            logger.error("لم يتم الاتصال بقاعدة البيانات.")
            return "فشل الاتصال بقاعدة البيانات."

        cursor = conn.cursor()

        # إضافة بيانات اللاعب
        cursor.execute("INSERT INTO players (name, progress) VALUES (%s, %s)", (player_name, player_progress))
        conn.commit()
        logger.info(f"تم حفظ بيانات اللاعب: {player_name} - {player_progress}")

        return jsonify(message="تم حفظ البيانات بنجاح")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء حفظ بيانات اللاعب: {e}")
        return jsonify(message="فشل في حفظ البيانات")
    finally:
        if conn:
            cursor.close()
            conn.close()

# إعداد Webhook للبوت
def set_webhook():
    """
    إعداد Webhook للبوت لتمرير التحديثات إلى التطبيق.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = f"https://twq-xzy4.onrender.com/webhook"  # تأكد من استبدال رابط التطبيق الخاص بك

    if not token or not webhook_url:
        logger.error("لم يتم العثور على رمز البوت أو الرابط الخاص بالـ Webhook في المتغيرات البيئية.")
        return

    url = f"https://api.telegram.org/bot{token}/setWebhook?url={webhook_url}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logger.info("تم تسجيل الـ Webhook بنجاح!")
        else:
            logger.error(f"فشل تسجيل الـ Webhook: {response.text}")
    except Exception as e:
        logger.error(f"حدث خطأ أثناء تسجيل الـ Webhook: {e}", exc_info=True)

# نقطة استقبال Webhook من Telegram
@app.route('/webhook', methods=['POST'])
def webhook():
    """
    استقبال التحديثات من Telegram عند استدعاء Webhook.
    """
    try:
        data = request.json
        # هنا يمكن معالجة البيانات المرسلة من Telegram
        logger.info(f"Received data: {data}")

        # تأكد من أن التحديث يحتوي على رسالة
        if 'message' in data:
            message = data['message']
            user_id = message['from']['id']
            user_name = message['from']['first_name']
            text = message['text']

            # على سبيل المثال: الرد على الرسالة
            response = {
                "chat_id": user_id,
                "text": f"مرحبًا {user_name}, لقد استلمت رسالتك: {text}"
            }
            send_message(response)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        logger.error(f"Error while processing the webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 400

# إرسال رسالة إلى Telegram باستخدام API
def send_message(response):
    """
    إرسال رسالة إلى Telegram باستخدام API.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        r = requests.post(url, data=response)
        if r.status_code != 200:
            logger.error(f"Error while sending message: {r.text}")
    except Exception as e:
        logger.error(f"Error while sending message: {e}", exc_info=True)

if __name__ == '__main__':
    set_webhook()  # إعداد Webhook عند بدء تشغيل التطبيق
    app.run(debug=True, host='0.0.0.0', port=10000)
