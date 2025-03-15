from flask import Flask, send_from_directory, request, jsonify
import os
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging

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

# مسار لمعالجة الويب هوك (Webhook)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info(f"Received data: {data}")
    try:
        user_id = data['message']['from']['id']
        name = data['message']['from'].get('first_name', 'Unknown')
        username = data['message']['from'].get('username', 'Unknown')
        photo = data['message'].get('photo', None)

        # تخزين البيانات في قاعدة البيانات
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)",
                               (name, photo[0]['file_id'] if photo else "default-avatar.png", 0))
                conn.commit()

        # تمرير البيانات إلى صفحة HTML
        player_data = {
            'name': name,
            'photo_url': photo[0]['file_id'] if photo else "default-avatar.png"
        }

        # عرض صفحة index.html من static
        return send_from_directory('static', 'index.html')

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the data."}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5001)))
