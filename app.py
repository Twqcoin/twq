import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging
import requests

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# وظيفة للاتصال بقاعدة البيانات
def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL is missing in the environment variables.")
            return None

        result = urlparse(database_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
        logger.info("Successfully connected to the database.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}", exc_info=True)
        return None

# دالة لتحميل الصورة عبر Telegram API باستخدام file_id
def get_photo_url(file_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    response = requests.get(url)
    file_path = response.json().get("result", {}).get("file_path", "")
    if file_path:
        return f"https://api.telegram.org/file/bot{token}/{file_path}"
    return None

# وظيفة لإنشاء الجدول إذا لم يكن موجودًا
def create_players_table():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255),
                        image_url VARCHAR(255),
                        progress INT
                    )
                ''')
                conn.commit()
                logger.info("Players table created successfully.")
        except Exception as e:
            logger.error(f"Error creating table: {e}", exc_info=True)
        finally:
            conn.close()

# مسار لعرض الصفحة الرئيسية من مجلد static
@app.route('/')
def home():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# مسار لمعالجة الويب هوك (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    create_players_table()  # إنشاء الجدول إذا لم يكن موجودًا

    data = request.get_json()
    logger.info(f"Received data: {data}")
    try:
        if 'message' not in data or 'from' not in data['message']:
            return jsonify({"error": "Invalid data format"}), 400

        user_id = data['message']['from']['id']
        name = data['message']['from'].get('first_name', 'Unknown')
        username = data['message']['from'].get('username', 'Unknown')
        photo = data['message'].get('photo', None)

        # الحصول على رابط الصورة الفعلي
        photo_url = get_photo_url(photo[0]['file_id']) if photo else "default-avatar.png"

        # حفظ البيانات في قاعدة البيانات
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)",
                               (name, photo_url, 0))
                conn.commit()
            conn.close()

        # تمرير البيانات إلى صفحة HTML
        player_data = {
            'name': name,
            'photo_url': photo_url
        }

        # عرض index.html مع تمرير البيانات
        return render_template('index.html', player_data=player_data)

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the data."}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
