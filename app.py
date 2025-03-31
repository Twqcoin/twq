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

app = Flask(__name__)

# إعداد مجلد حفظ الصور
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # إنشاء المجلد إذا لم يكن موجوداً
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
        # تحميل الصورة
        response = requests.get(file_url, stream=True)
        if response.status_code == 200:
            # إعداد اسم الملف
            filename = f"{user_id}.jpg"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # حفظ الصورة في المجلد
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except Exception as e:
        logger.error(f"Error saving photo for user {user_id}: {e}", exc_info=True)
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
                        user_id BIGINT UNIQUE,
                        name VARCHAR(255),
                        username VARCHAR(255),
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

# مسار لعرض الصفحة الرئيسية
@app.route('/')
def home():
    # استخراج بيانات المستخدم من query parameters
    query_string = request.query_string.decode('utf-8')
    params = parse_qs(query_string)
    
    user_id = params.get('user_id', [None])[0]
    name = params.get('name', ['Unknown'])[0]
    username = params.get('username', ['Unknown'])[0]
    photo_url = params.get('photo', [None])[0]
    
    # حفظ بيانات المستخدم في الجلسة أو قاعدة البيانات إذا لزم الأمر
    logger.info(f"User accessed home page: {name} (ID: {user_id})")
    
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# مسار لمعالجة الويب هوك (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    create_players_table()
    data = request.get_json()
    logger.info(f"Received webhook data: {data}")
    
    try:
        if not isinstance(data, dict):
            logger.error("Invalid data format")
            return jsonify({"error": "Invalid data format"}), 400

        # استخراج بيانات المستخدم من الطلب
        user_id = data.get('user_id') or (data.get('from', {}).get('id') if 'from' in data else None)
        name = data.get('name') or (data.get('from', {}).get('first_name', 'Unknown') if 'from' in data else 'Unknown')
        username = data.get('username') or (data.get('from', {}).get('username', 'Unknown') if 'from' in data else 'Unknown')
        photo = data.get('photo') or (data.get('photo_url') or 'default-avatar.png')

        if not user_id:
            logger.error("User ID not provided")
            return jsonify({"error": "User ID is required"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500

        try:
            with conn.cursor() as cursor:
                # التحقق من وجود المستخدم في قاعدة البيانات
                cursor.execute("SELECT name, image_url FROM players WHERE user_id = %s", (user_id,))
                existing_player = cursor.fetchone()
                
                photo_url = photo
                if photo and not photo.startswith(('http', '/')):
                    # إذا كانت photo عبارة عن file_id من Telegram
                    file_url = get_photo_url(photo)
                    if file_url:
                        saved_filename = save_photo(file_url, user_id)
                        if saved_filename:
                            photo_url = f"/uploads/{saved_filename}"

                if existing_player:
                    # تحديث بيانات المستخدم إذا تغيرت
                    if existing_player[0] != name or existing_player[1] != photo_url:
                        cursor.execute(
                            "UPDATE players SET name = %s, username = %s, image_url = %s WHERE user_id = %s",
                            (name, username, photo_url, user_id))
                        conn.commit()
                        logger.info(f"Updated player data for user {user_id}")
                else:
                    # إضافة مستخدم جديد
                    cursor.execute(
                        "INSERT INTO players (user_id, name, username, image_url, progress) VALUES (%s, %s, %s, %s, %s)",
                        (user_id, name, username, photo_url, 0))
                    conn.commit()
                    logger.info(f"Added new player: {name} (ID: {user_id})")

                player_data = {
                    "user_id": user_id,
                    "name": name,
                    "username": username,
                    "photo_url": photo_url if photo_url else "default-avatar.png"
                }
                
                logger.info(f"Player data processed: {player_data}")
                return jsonify({
                    "status": "success",
                    "message": "Data processed successfully",
                    "player_data": player_data
                })
                
        except Exception as e:
            logger.error(f"Database error: {e}", exc_info=True)
            return jsonify({"error": "Database operation failed"}), 500
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the request"}), 500

# مسار للحصول على بيانات اللاعب
@app.route('/get_player_data', methods=['GET'])
def get_player_data():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, username, image_url FROM players WHERE user_id = %s", (user_id,))
            player = cursor.fetchone()
            
            if player:
                return jsonify({
                    "status": "success",
                    "player_data": {
                        "name": player[0],
                        "username": player[1],
                        "photo_url": player[2] if player[2] else "default-avatar.png"
                    }
                })
            else:
                return jsonify({"error": "Player not found"}), 404
    except Exception as e:
        logger.error(f"Database error: {e}", exc_info=True)
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        conn.close()

# مسار لعرض الصور المخزنة
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # إنشاء مجلد التحميلات إذا لم يكن موجوداً
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
