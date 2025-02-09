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
    data = request.get_json()
    logger.info(f"Received data: {data}")

    try:
        # Extract user parameters from incoming data
        user_id = data['message']['from']['id']
        name = data['message']['from'].get('first_name', 'Unknown')  # User's first name
        username = data['message']['from'].get('username', 'Unknown')  # User's Telegram username
        photo = data['message'].get('photo', None)  # User's profile photo (if available)

        # Log the received data
        logger.info(f"User ID: {user_id}, Name: {name}, Username: {username}, Photo: {photo}")

        # Store the player information in the database
        conn = get_db_connection()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO players (name, image_url, progress) VALUES (%s, %s, %s)",
                               (name, photo[0]['file_id'] if photo else "default-avatar.png", 0))
                conn.commit()

        return jsonify({
            "status": "success",
            "user_id": user_id,
            "name": name,
            "username": username,
            "photo": photo[0]['file_id'] if photo else "No photo provided"
        }), 200

    except KeyError as e:
        logger.error(f"Missing key in incoming data: {e}", exc_info=True)
        return jsonify({"error": f"Missing data: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return jsonify({"error": "An error occurred while processing the data."}), 500

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

# Route to retrieve player progress
@app.route('/get_progress', methods=['POST'])  # Changed method to POST
def get_progress():
    data = request.get_json()
    if 'name' not in data:
        return jsonify({"error": "Name is required."}), 400
    player_name = data['name']
    progress = get_player_progress(player_name)
    if progress is None:
        return jsonify({"error": "Player not found."}), 404
    return jsonify({"name": player_name, "progress": progress}), 200

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
    # Ensure the correct path for static files in production
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)

if __name__ == '__main__':
    create_db()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
