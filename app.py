import os
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging
import requests  # إضافة مكتبة requests لإعداد Webhook
import telegram  # إضافة مكتبة التليجرام

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')  # تعريف مجلد static لتخزين ملفات Unity

# إعداد اتصال بقاعدة بيانات PostgreSQL
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
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
        return conn
    except Exception as e:
        logger.error(f"فشل الاتصال بقاعدة البيانات: {e}", exc_info=True)
        return None

# إنشاء قاعدة البيانات (إذا لم تكن موجودة)
def create_db():
    """
    إنشاء جدول players إذا لم يكن موجودًا.
    """
    try:
        conn = get_db_connection()
        if conn is None:
            return
        with conn.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                                id SERIAL PRIMARY KEY,
                                name TEXT NOT NULL,
                                image_url TEXT NOT NULL,
                                progress INTEGER DEFAULT 0)''')
            conn.commit()
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إنشاء الجدول: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# إضافة نقطة النهاية الخاصة بالـ Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """
    هذه النقطة تستقبل الرسائل من تيليجرام عند إرسال المستخدمين لها.
    """
    data = request.get_json()
    logger.info(f"Received data: {data}")
    
    # الحصول على chat_id من البيانات الواردة من تيليجرام
    chat_id = data['message']['chat']['id']
    
    # استرجاع بيانات اللاعب من قاعدة البيانات
    player_name = data['message']['text']
    player_image_url = get_player_image_url(player_name)
    
    if player_image_url:
        send_player_info(player_name, player_image_url, chat_id)
    else:
        send_message(chat_id, f"لا يوجد لاعب بهذا الاسم: {player_name}")
    
    return jsonify({"status": "success"}), 200

# إرسال معلومات اللاعب
def send_player_info(player_name, player_image_url, chat_id):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telegram.Bot(token=bot_token)
    
    # إرسال صورة واسم اللاعب
    bot.send_photo(chat_id=chat_id, photo=player_image_url, caption=f"Player: {player_name}")

# إرسال رسالة
def send_message(chat_id, text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=text)

# إعداد Webhook للبوت عند بدء التشغيل
def set_webhook():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # استبدل بمفتاح البوت الخاص بك
    webhook_url = os.getenv("WEBHOOK_URL")  # تحديد الرابط الخاص بالـ Webhook
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}/webhook"
    response = requests.post(url)
    if response.status_code == 200:
        logger.info("Webhook has been set successfully!")
    else:
        logger.error(f"Failed to set webhook: {response.text}")

# استرجاع صورة اللاعب من قاعدة البيانات
def get_player_image_url(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT image_url FROM players WHERE name = %s", (player_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع صورة اللاعب: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# إضافة لاعب إلى قاعدة البيانات
@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.get_json()
    if 'name' not in data or 'image_url' not in data:
        return jsonify({"error": "الاسم ورابط الصورة مطلوبان."}), 400
    player_name = data['name']
    player_image_url = data['image_url']
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "فشل الاتصال بقاعدة البيانات."}), 500
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                           (player_name, player_image_url, 0))
            conn.commit()
        return jsonify({"message": f"تم إضافة اللاعب {player_name} بنجاح!"}), 201
    except Exception as e:
        logger.error(f"حدث خطأ أثناء إضافة اللاعب: {e}", exc_info=True)
        return jsonify({"error": "حدث خطأ أثناء إضافة اللاعب."}), 500
    finally:
        if conn:
            conn.close()

# استرجاع بيانات لاعب
@app.route('/get_player/<name>', methods=['GET'])
def get_player(name):
    player_image_url = get_player_image_url(name)
    if player_image_url is None:
        return jsonify({"error": "لا يوجد لاعب بهذا الاسم."}), 404
    return jsonify({"name": name, "image_url": player_image_url}), 200

# استرجاع تقدم لاعب عبر API
@app.route('/get_progress', methods=['POST'])
def get_progress():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "الاسم مطلوب."}), 400
    player_name = data['name']
    progress = get_player_progress(player_name)
    if progress is None:
        return jsonify({"error": "لا يوجد لاعب بهذا الاسم."}), 404
    return jsonify({"name": player_name, "progress": progress}), 200

# دالة لاسترجاع تقدم اللاعب
def get_player_progress(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT progress FROM players WHERE name = %s", (player_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع تقدم اللاعب: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# بدء التعدين
@app.route('/start-mining', methods=['POST'])
def start_mining():
    data = request.get_json()
    if 'userId' not in data:
        return jsonify({"error": "User ID is required."}), 400

    user_id = data['userId']
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500
        with conn.cursor() as cursor:
            cursor.execute("UPDATE players SET progress = progress + 1 WHERE name = %s", (user_id,))
            conn.commit()
        return jsonify({"message": f"Mining started for user {user_id}!"}), 200
    except Exception as e:
        logger.error(f"Error during mining start: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while starting mining."}), 500
    finally:
        if conn:
            conn.close()

# فتح تطبيق Unity WebGL بدلاً من رسالة JSON
@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))  # إعادة توجيه المستخدم إلى Unity

# تمكين فتح ملفات Unity WebGL مباشرة
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    create_db()
    set_webhook()  # إعداد Webhook عند بدء التطبيق
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
