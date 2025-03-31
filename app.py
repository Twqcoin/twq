import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse, parse_qs
import logging
import requests
from werkzeug.utils import secure_filename

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات التسجيل (Logging)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

# إعداد مجلد حفظ الصور
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# وظيفة للاتصال بقاعدة البيانات
def get_db_connection():
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL is missing in environment variables")
            return None

        result = urlparse(database_url)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port or 5432
        )
        logger.info("Connected to database successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        return None

# دالة لتحميل الصورة من Telegram
def get_photo_url(file_id):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Telegram bot token not configured")
        return None

    url = f"https://api.telegram.org/bot{token}/getFile?file_id={file_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_path = response.json().get("result", {}).get("file_path")
        if file_path:
            return f"https://api.telegram.org/file/bot{token}/{file_path}"
        logger.warning("No file path in Telegram response")
    except Exception as e:
        logger.error(f"Failed to get photo URL: {e}", exc_info=True)
    return None

# دالة لحفظ الصورة محلياً
def save_photo(file_url, user_id):
    try:
        response = requests.get(file_url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = f"{user_id}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        logger.error(f"Error saving photo: {e}", exc_info=True)
    return None

# إنشاء جدول اللاعبين
def create_players_table():
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT UNIQUE,
                    name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    image_url VARCHAR(255) NOT NULL,
                    progress INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("Players table created/verified")
            return True
    except Exception as e:
        logger.error(f"Error creating table: {e}", exc_info=True)
        return False
    finally:
        conn.close()

# مسار الصفحة الرئيسية
@app.route('/')
def home():
    params = parse_qs(request.query_string.decode('utf-8'))
    
    user_id = params.get('user_id', [None])[0]
    name = params.get('name', ['Guest'])[0]
    username = params.get('username', ['guest'])[0]
    photo_url = params.get('photo', ['/static/default-avatar.png'])[0]

    logger.info(f"User accessed: {name} (ID: {user_id})")
    return send_from_directory('static', 'index.html')

# مسار الويب هوك
@app.route('/webhook', methods=['POST'])
def webhook():
    create_players_table()
    data = request.get_json()
    
    if not isinstance(data, dict):
        return jsonify({"error": "Invalid data format"}), 400

    try:
        # استخراج البيانات الأساسية
        user_data = data.get('from', {})
        user_id = data.get('user_id') or user_data.get('id')
        name = data.get('name') or user_data.get('first_name', 'Unknown')
        username = data.get('username') or user_data.get('username', 'unknown')
        photo = data.get('photo') or data.get('photo_url')

        if not user_id:
            return jsonify({"error": "User ID required"}), 400

        # معالجة الصورة
        photo_url = '/static/default-avatar.png'
        if photo:
            if isinstance(photo, list) and photo[0].get('file_id'):
                file_url = get_photo_url(photo[0]['file_id'])
                if file_url:
                    saved_file = save_photo(file_url, user_id)
                    if saved_file:
                        photo_url = f'/uploads/{saved_file}'
            elif photo.startswith(('http', '/')):
                photo_url = photo

        # حفظ/تحديث البيانات في DB
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database error"}), 500

        with conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO players (user_id, name, username, image_url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    username = EXCLUDED.username,
                    image_url = EXCLUDED.image_url,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING *
            ''', (user_id, name, username, photo_url))
            
            conn.commit()
            player = cursor.fetchone()
            
        return jsonify({
            "status": "success",
            "player_data": {
                "user_id": user_id,
                "name": name,
                "username": username,
                "photo_url": photo_url
            }
        })

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

# مسار بيانات اللاعب
@app.route('/get_player_data', methods=['GET'])
def get_player_data():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID required"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database error"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute('''
                SELECT name, username, image_url 
                FROM players 
                WHERE user_id = %s
            ''', (user_id,))
            
            player = cursor.fetchone()
            if player:
                return jsonify({
                    "status": "success",
                    "player_data": {
                        "name": player[0],
                        "username": player[1],
                        "photo_url": player[2] or '/static/default-avatar.png'
                    }
                })
            return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        logger.error(f"Player data error: {e}", exc_info=True)
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

# مسار الملفات المحملة
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return send_from_directory('static', 'default-avatar.png')

# مسار الصورة الافتراضية
@app.route('/static/default-avatar.png')
def default_avatar():
    return send_from_directory('static', 'default-avatar.png')

if __name__ == '__main__':
    create_players_table()
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
