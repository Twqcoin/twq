import os
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging

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

# استرجاع تقدم لاعب
def get_player_progress(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT progress FROM players WHERE name = %s", (player_name,))
            progress = cursor.fetchone()
            return progress[0] if progress else 0
    except Exception as e:
        logger.error(f"حدث خطأ أثناء استرجاع التقدم: {e}", exc_info=True)
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
    progress = get_player_progress(name)
    if progress is None:
        return jsonify({"error": "لا يوجد لاعب بهذا الاسم."}), 404
    return jsonify({"name": name, "progress": progress}), 200

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
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
