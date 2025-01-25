from flask import Flask, render_template, jsonify, g, request
import psycopg2
import os
from dotenv import load_dotenv
from celery import Celery
import requests
import logging

# Load environment variables from .env file
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# Celery configuration
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection setup
def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
    return g.db

# Function to send message to Telegram
def send_message_to_telegram(chat_id, player_name, player_image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("Telegram bot token is missing.")
        return {"error": "Telegram bot token is missing."}

    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    message = f"Player Name: {player_name}"

    payload = {
        "chat_id": chat_id,
        "caption": message,
        "photo": player_image_url
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        logger.error(f"Error sending message: {response.text}")
    else:
        logger.info(f"Message sent successfully to chat_id {chat_id} for player {player_name}.")
    return response.json()

# Route to receive player data
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

        # Store data in the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO players (name, image_url) VALUES (%s, %s) RETURNING id;", (player_name, player_image_url))
        player_id = cursor.fetchone()[0]
        connection.commit()
        cursor.close()

        # Send data to Telegram
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not chat_id:
            raise ValueError("Telegram chat ID is missing.")

        send_message_to_telegram(chat_id, player_name, player_image_url)

        return jsonify({"status": "success", "message": f"Player data received and sent to Telegram with ID {player_id}."}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to list all players
@app.route("/players", methods=["GET"])
def get_players():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id, name, image_url FROM players;")
        players = cursor.fetchall()
        cursor.close()

        players_list = [{"id": player[0], "name": player[1], "image_url": player[2]} for player in players]
        return jsonify(players_list), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Route to send specific player info to Telegram
@app.route("/send_player_info/<int:player_id>/<chat_id>", methods=["GET"])
def send_player_info(player_id, chat_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT name, image_url FROM players WHERE id = %s;", (player_id,))
        player = cursor.fetchone()
        cursor.close()

        if not player:
            return jsonify({"status": "error", "message": "Player not found."}), 404

        player_name, player_image_url = player
        response = send_message_to_telegram(chat_id, player_name, player_image_url)

        return jsonify({"status": "success", "message": f"Player {player_name} info sent to Telegram.", "response": response}), 200
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Index route
@app.route("/")
def index():
    return render_template("index.html")

# Teardown to close database connection
@app.teardown_appcontext
def close_connection(exception):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
