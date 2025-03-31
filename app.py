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

if __name__ == '__main__':
    create_players_table()
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)
