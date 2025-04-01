import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging
import requests
from werkzeug.utils import secure_filename

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# إعداد مجلد حفظ الصور
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_path = response.json().get("result", {}).get("file_path", "")
        if file_path:
            return f"https://api.telegram.org/file/bot{token}/{file_path}"
        else:
            logger.warning("No file path found in the response.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get photo URL: {e}", exc_info=True)
    return None

# دالة لحفظ الصورة في المجلد static/uploads
def save_photo(file_url, user_id):
    try:
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            filename = f"{user_id}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        logger.error(f"Error saving photo for user {user_id}: {e}", exc_info=True)
    return None

# إنشاء الجدول إذا لم يكن موجودًا
def create_players_table():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE,
                    name VARCHAR(255),
                    image_url VARCHAR(255),
                    progress INT DEFAULT 0
                )''')
                conn.commit()
                logger.info("Players table created successfully.")
        except Exception as e:
            logger.error(f"Error creating table: {e}", exc_info=True)
        finally:
            conn.close()

# مسار لعرض الصفحة الرئيسية
@app.route('/')
def home():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# مسار لمعالجة البيانات القادمة من Telegram Webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    create_players_table()
    data = request.get_json()
    logger.info(f"Received data: {data}")
    try:
        if not isinstance(data, dict) or 'from' not in data:
            return jsonify({"error": "Invalid data format"}), 400

        user_id = data['from']['id']
        name = data['from'].get('first_name', 'Unknown')
        photo = data.get('photo', None)
        conn = get_db_connection()
        player_data = {"name": name, "photo_url": "https://minqx.onrender.com/static/default-avatar.png"}  # رابط جديد

        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT name, image_url FROM players WHERE user_id = %s", (user_id,))
                    existing_player = cursor.fetchone()
                    
                    if existing_player:
                        player_data["name"] = existing_player[0]
                        player_data["photo_url"] = existing_player[1] if existing_player[1] else "https://minqx.onrender.com/static/default-avatar.png"  # رابط جديد
                    else:
                        photo_url = "https://minqx.onrender.com/static/default-avatar.png"  # رابط جديد
                        if photo:
                            file_url = get_photo_url(photo[0]['file_id'])
                            if file_url:
                                photo_url = save_photo(file_url, user_id) or "https://minqx.onrender.com/static/default-avatar.png"  # رابط جديد
                        cursor.execute("INSERT INTO players (user_id, name, image_url) VALUES (%s, %s, %s)",
                                       (user_id, name, photo_url))
                        conn.commit()
                        player_data["photo_url"] = photo_url
            except Exception as e:
                logger.error(f"Error handling player data: {e}", exc_info=True)
            finally:
                conn.close()
        return jsonify({"status": "success", "player_data": player_data})
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the data."}), 500

# مسار لعرض الصور المخزنة
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
