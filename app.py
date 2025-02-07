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

# نقطة النهاية لبدء التعدين
@app.route('/start-mining', methods=['POST'])
def start_mining():
    data = request.get_json()
    if 'userId' not in data:
        return jsonify({"error": "المعرف مطلوب."}), 400

    user_id = data['userId']

    # محاكاة عملية التعدين (يمكنك إضافة الكود الفعلي هنا)
    logger.info(f"تم بدء التعدين للمستخدم: {user_id}")

    return jsonify({"message": "تم بدء التعدين بنجاح!"}), 200

# نقطة النهاية لإضافة إحالة
@app.route('/add-referral', methods=['POST'])
def add_referral():
    data = request.get_json()
    if 'userId' not in data:
        return jsonify({"error": "المعرف مطلوب."}), 400

    user_id = data['userId']

    # إضافة الإحالة إلى قاعدة البيانات أو المحاكاة
    logger.info(f"تم إضافة إحالة للمستخدم: {user_id}")

    return jsonify({"message": "تم إضافة الإحالة بنجاح!"}), 200

# فتح تطبيق Unity WebGL بدلاً من رسالة JSON
@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))  # إعادة توجيه المستخدم إلى Unity

# تمكين فتح ملفات Unity WebGL مباشرة
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
