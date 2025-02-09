import os
from flask import Flask, request, jsonify, redirect, url_for, send_from_directory
from dotenv import load_dotenv
import psycopg2
from urllib.parse import urlparse
import logging
import requests  # Adding requests library for Webhook setup
import telegram  # Adding telegram library for bot integration

# Load environment variables
load_dotenv()

# Setup logging for error tracking
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')  # Define static folder for Unity files

# Database connection setup
def get_db_connection():
    """
    Creates a connection to the PostgreSQL database using DATABASE_URL from environment variables.
    """
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
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}", exc_info=True)
        return None

# Database table creation (if not exists)
def create_db():
    """
    Creates the 'players' table if it doesn't exist.
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
        logger.error(f"Error creating table: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()

# Webhook route to receive messages from Telegram users
@app.route('/webhook', methods=['POST'])
def webhook():
    """
    This endpoint receives messages from Telegram when users send messages to the bot.
    """
    data = request.get_json()
    logger.info(f"Received data: {data}")

    try:
        # Extract user parameters from incoming data
        user_id = data['message']['from']['id']
        name = data['message']['from'].get('first_name', 'Unknown')  # User's first name (if available)
        username = data['message']['from'].get('username', 'Unknown')  # User's Telegram username (if available)
        photo = data['message'].get('photo', None)  # User's profile photo (if available)

        # Log the received data
        logger.info(f"User ID: {user_id}, Name: {name}, Username: {username}, Photo: {photo}")

        # Return received data as confirmation
        return jsonify({
            "status": "success",
            "user_id": user_id,
            "name": name,
            "username": username,
            "photo": photo if photo else "No photo provided"
        }), 200

    except KeyError as e:
        logger.error(f"Missing key in incoming data: {e}", exc_info=True)
        return jsonify({"error": f"Missing data: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the data."}), 500

# Function to send player information to Telegram
def send_player_info(player_name, player_image_url, chat_id):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telegram.Bot(token=bot_token)
    
    # Send player image and name
    bot.send_photo(chat_id=chat_id, photo=player_image_url, caption=f"Player: {player_name}")

# Function to send a message to a user on Telegram
def send_message(chat_id, text):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = telegram.Bot(token=bot_token)
    bot.send_message(chat_id=chat_id, text=text)

# Set up the Webhook for the bot at startup
def set_webhook():
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Replace with your bot token
    webhook_url = os.getenv("WEBHOOK_URL")  # Set the Webhook URL here
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}/webhook"
    response = requests.post(url)
    if response.status_code == 200:
        logger.info("Webhook has been set successfully!")
    else:
        logger.error(f"Failed to set webhook: {response.text}")

# Function to retrieve a player's image URL from the database
def get_player_image_url(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT image_url FROM players WHERE name = %s", (player_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error retrieving player image: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# Route to add a new player to the database
@app.route('/add_player', methods=['POST'])
def add_player():
    data = request.get_json()
    if 'name' not in data or 'image_url' not in data:
        return jsonify({"error": "Name and image URL are required."}), 400
    player_name = data['name']
    player_image_url = data['image_url']
    
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Failed to connect to the database."}), 500
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)", 
                           (player_name, player_image_url, 0))
            conn.commit()
        return jsonify({"message": f"Player {player_name} added successfully!"}), 201
    except Exception as e:
        logger.error(f"Error adding player: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while adding the player."}), 500
    finally:
        if conn:
            conn.close()

# Route to retrieve a player's data
@app.route('/get_player/<name>', methods=['GET'])
def get_player(name):
    player_image_url = get_player_image_url(name)
    if player_image_url is None:
        return jsonify({"error": "Player not found."}), 404
    return jsonify({"name": name, "image_url": player_image_url}), 200

# Route to retrieve player progress
@app.route('/get_progress', methods=['POST'])
def get_progress():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "Name is required."}), 400
    player_name = data['name']
    progress = get_player_progress(player_name)
    if progress is None:
        return jsonify({"error": "Player not found."}), 404
    return jsonify({"name": player_name, "progress": progress}), 200

# Function to retrieve player progress from the database
def get_player_progress(player_name):
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        with conn.cursor() as cursor:
            cursor.execute("SELECT progress FROM players WHERE name = %s", (player_name,))
            result = cursor.fetchone()
            return result[0] if result else None
    except Exception as e:
        logger.error(f"Error retrieving player progress: {e}", exc_info=True)
        return None
    finally:
        if conn:
            conn.close()

# Route to start mining (increase progress)
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

# Serve Unity WebGL files
@app.route('/')
def index():
    return redirect(url_for('static', filename='index.html'))  # Redirect to Unity WebGL index

# Enable serving static Unity WebGL files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    create_db()
    set_webhook()  # Set webhook on startup
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
