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

# إعداد الاتصال بقاعدة البيانات PostgreSQL بدون شهادات SSL
def get_db_connection():
    attempts = 5
    conn = None
    while attempts > 0:
        try:
            if not DATABASE_URL:
                logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
                return None

            result = urlparse(DATABASE_URL)

            # تعديل الاتصال بقاعدة البيانات بدون تمكين SSL
            conn = psycopg2.connect(
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
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
        finally:
            if conn:
                conn.close()

# نقطة لاسترجاع بيانات اللاعب
@app.route('/get-player/<player_name>')
def get_player(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify(message="فشل الاتصال بقاعدة البيانات.")

        with conn.cursor() as cursor:
            # استرجاع بيانات اللاعب
            cursor.execute("SELECT * FROM players WHERE name = %s", (player_name,))
            player_data = cursor.fetchone()

            if player_data:
                player_name = player_data[1]  # الاسم
                player_progress = player_data[2]  # النقاط
                return jsonify(name=player_name, progress=player_progress)
            else:
                return jsonify(message="لا يوجد لاعب بهذا الاسم")

    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع بيانات اللاعب: {e}")
        return jsonify(message="فشل في استرجاع البيانات")
    finally:
        if conn:
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
        return jsonify({"status":"error", "message": str(e)}), 400

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
