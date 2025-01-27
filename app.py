from flask import Flask, render_template, request, jsonify
from celery import Celery
import os
import requests
import psycopg2
from urllib.parse import urlparse
import logging

# تهيئة Flask
app = Flask(__name__)

# تهيئة السجل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تعيين عنوان Redis من المتغيرات البيئية
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# تهيئة Celery
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

# إعداد الاتصال بقاعدة البيانات PostgreSQL
def get_db_connection():
    """
    إنشاء اتصال بقاعدة البيانات باستخدام DATABASE_URL من المتغيرات البيئية.
    """
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
            return None

        result = urlparse(database_url)
        logger.info(f"محاولة الاتصال بقاعدة البيانات: {result.hostname}, {result.path[1:]}")

        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        logger.info("تم الاتصال بقاعدة البيانات بنجاح!")
        return conn
    except Exception as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {e}", exc_info=True)
        return None

# تحديث تقدم اللاعب في قاعدة البيانات
def update_player_progress(player_name, progress):
    """
    تحديث تقدم لاعب في قاعدة البيانات.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE players SET progress = %s WHERE name = %s", (progress, player_name))
                conn.commit()
                logger.info(f"تم تحديث تقدم اللاعب {player_name} إلى {progress}%")
        except Exception as e:
            logger.error(f"خطأ في تحديث تقدم اللاعب: {e}", exc_info=True)
        finally:
            conn.close()

# إرسال رسالة عبر Telegram
@celery.task
def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"تم إرسال الرسالة إلى Telegram: {message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"خطأ في إرسال الرسالة: {e}", exc_info=True)

# مسار لتحديث تقدم اللاعب
@app.route('/update_progress', methods=['POST'])
def update_progress():
    player_name = request.json.get('name')
    progress = request.json.get('progress')

    if not player_name or not progress:
        return jsonify({"error": "Missing player name or progress"}), 400

    # تحديث تقدم اللاعب في قاعدة البيانات
    update_player_progress(player_name, progress)

    # إرسال إشعار إلى Telegram
    send_telegram_message.delay(f"Player {player_name} progress updated to {progress}%")

    return jsonify({"message": "Progress updated successfully!"})

# مسار الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')  # يعرض ملف HTML من مجلد templates

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
