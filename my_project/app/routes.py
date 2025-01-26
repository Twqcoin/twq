from flask import jsonify, request, g
from app import app
import psycopg2
import os
import requests
import logging

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# الاتصال بقاعدة البيانات
def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    return g.db

# استقبال بيانات اللاعب
@app.route("/api/receive_player_data", methods=["POST"])
def receive_player_data():
    try:
        data = request.json
        if not data:
            raise ValueError("No data received.")

        player_name = data.get('name')
        player_image_url = data.get('image_url')

        if not player_name or not player_image_url:
            raise ValueError("Player name or image URL is missing.")

        # تخزين البيانات في قاعدة البيانات
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO players (name, image_url) VALUES (%s, %s) RETURNING id;", (player_name, player_image_url))
        player_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()

        # إرسال البيانات إلى Telegram
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id:
            raise ValueError("Telegram chat ID is missing.")

        send_message_to_telegram(chat_id, player_name, player_image_url)

        return jsonify({"status": "success", "message": f"Player data received and sent to Telegram with ID {player_id}."}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# إغلاق الاتصال بقاعدة البيانات
@app.teardown_appcontext
def close_connection(exception):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()
