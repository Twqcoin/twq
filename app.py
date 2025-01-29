from flask import Flask, render_template, request, jsonify
from celery import Celery
import os
import requests
import psycopg2
from urllib.parse import urlparse
import logging
import certifi
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# تهيئة Flask
app = Flask(__name__)

# إعداد سجلات التتبع
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة Celery مع Redis كوسيط
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

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
    try:
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL غير موجود في المتغيرات البيئية.")
            return None

        result = urlparse(database_url)
        db_port = os.getenv("DB_PORT", 5432)
        
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host="postgres",  # استخدام اسم الخدمة الداخلية لـ PostgreSQL
            port=db_port,
            sslmode='require',
            sslrootcert=certifi.where()
        )
        logger.info("Connected to PostgreSQL database successfully.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

# اختبار الاتصال بقاعدة البيانات
def test_db_connection():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                logger.info("Database connection test successful!")
            conn.close()
        except Exception as e:
            logger.error(f"Error testing database connection: {e}")
    else:
        logger.error("Failed to connect to the database!")

# إنشاء الجداول إذا لم تكن موجودة
def create_tables():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    progress INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL,
                    reward INT,
                    is_completed BOOLEAN DEFAULT FALSE,
                    player_id INT REFERENCES players(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)

                conn.commit()
                logger.info("Tables created successfully (if not already exist).")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
        finally:
            conn.close()

# تحديث تقدم اللاعب في قاعدة البيانات
def update_player_progress(player_name, progress):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE players SET progress = %s WHERE name = %s", (progress, player_name))
                conn.commit()
                logger.info(f"Player progress updated for {player_name} to {progress}%.")
        except Exception as e:
            logger.error(f"Error updating player progress: {e}")
        finally:
            conn.close()

# إرسال رسالة عبر Telegram
@celery.task
def send_telegram_message(message):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        logger.error("Telegram bot token or chat ID is missing!")
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logger.info(f"Message sent to Telegram: {message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message: {e}")

# مسار لتحديث تقدم اللاعب
@app.route('/update_progress', methods=['POST'])
def update_progress():
    player_name = request.json.get('name')
    progress = request.json.get('progress')
    
    if not player_name or not progress:
        return jsonify({"error": "Missing player name or progress"}), 400
    
    try:
        progress = int(progress)
        if progress < 0 or progress > 100:
            return jsonify({"error": "Progress must be between 0 and 100"}), 400
    except ValueError:
        return jsonify({"error": "Progress must be a number"}), 400

    update_player_progress(player_name, progress)
    send_telegram_message.delay(f"Player {player_name} progress updated to {progress}%")
    return jsonify({"message": "Progress updated successfully!"})

# الصفحة الرئيسية
@app.route('/')
def home():
    logger.info("Rendering the home page.")
    return render_template('index.html')

if __name__ == '__main__':
    test_db_connection()
    create_tables()
    logger.info("Starting the Flask application...")
    app.run(debug=True, host='0.0.0.0', port=10000)
