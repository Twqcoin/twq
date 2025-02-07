import os
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد تسجيل الأخطاء
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')  # تعريف مجلد static لتخزين ملفات Unity

# إعداد اتصال بقاعدة بيانات PostgreSQL
def get_db_connection():
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

# تعديل المسار "start-mining" للبوت
@app.route('/start-mining', methods=['POST'])
def start_mining():
    data = request.get_json()
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId مطلوب."}), 400

    # هنا يتم معالجة البدء في التعدين
    logger.info(f"بدأ التعدين للمستخدم {user_id}")
    return jsonify({"message": "التعدين بدأ بنجاح!"}), 200

# إضافة مسار لإضافة الإحالة
@app.route('/add-referral', methods=['POST'])
def add_referral():
    data = request.get_json()
    user_id = data.get("userId")
    if not user_id:
        return jsonify({"error": "userId مطلوب."}), 400

    # هنا يتم معالجة إضافة الإحالة
    logger.info(f"تمت إضافة إحالة للمستخدم {user_id}")
    return jsonify({"message": "تم إضافة الإحالة بنجاح!"}), 200

# إعادة توجيه المستخدم إلى Unity WebGL
@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))  # إعادة توجيه المستخدم إلى Unity

# تمكين فتح ملفات Unity WebGL مباشرة
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
