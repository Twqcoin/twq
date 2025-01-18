from flask import Flask, render_template, jsonify, g
import psycopg2
import os
from dotenv import load_dotenv
from celery import Celery
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Celery configuration to use Redis
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')  # Using Redis as broker
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')  # Store result in Redis

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Database connection setup
def get_db_connection():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "game_db"),
            user=os.getenv("DB_USER", "your_user"),
            password=os.getenv("DB_PASSWORD", "your_password")
        )
    return g.db

# Function to send player info to Telegram
def send_message_to_telegram(chat_id, player_name, player_image_url):
    token = os.getenv("TELEGRAM_BOT_TOKEN")  # تأكد من أن هذا هو التوكن الصحيح للبوت
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    message = f"Player Name: {player_name}"

    payload = {
        "chat_id": chat_id,
        "caption": message,
        "photo": player_image_url  # تأكد من إضافة الرابط الصحيح للصورة
    }

    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Error sending message: {response.text}")
    return response

# Route to display players
@app.route("/players", methods=["GET"])
def get_players():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM players;")
        players = cursor.fetchall()
        players_list = [{"id": player[0], "name": player[1], "image_url": player[2]} for player in players]
        return jsonify(players_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Route to send player data to Telegram (use this for testing)
@app.route("/send_player_info/<int:player_id>/<chat_id>", methods=["GET"])
def send_player_info(player_id, chat_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name, image_url FROM players WHERE id = %s;", (player_id,))
        player = cursor.fetchone()
        if player:
            player_name, player_image_url = player
            send_message_to_telegram(chat_id, player_name, player_image_url)
            return jsonify({"message": f"Player {player_name} info sent to Telegram."}), 200
        else:
            return jsonify({"error": "Player not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()

# Index page route
@app.route("/")
def index():
    # Use the correct path for the static files (Unity WebGL)
    return render_template("index.html")

# Close the database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    connection = g.pop('db', None)
    if connection is not None:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
