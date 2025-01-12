from flask import Flask, render_template, jsonify, g
import psycopg2
import os
from dotenv import load_dotenv
from celery import Celery  # Import Celery directly
import psycopg2

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Celery configuration to use PostgreSQL
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'postgresql://your_user:your_password@localhost/your_db')  # Using PostgreSQL as broker
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'postgresql://your_user:your_password@localhost/your_db')  # Store result in PostgreSQL

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Database connection setup
def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "game_db"),
            user=os.getenv("DB_USER", "your_user"),
            password=os.getenv("DB_PASSWORD", "your_password")
        )
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# Route to display players
@app.route("/players", methods=["GET"])
def get_players():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Unable to connect to database"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM players;")
        players = cursor.fetchall()
        players_list = [{"id": player[0], "name": player[1]} for player in players]
        return jsonify(players_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Index page route
@app.route("/")
def index():
    return render_template("index.html")

# Close the database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    connection = getattr(g, 'db', None)
    if connection is not None:
        connection.close()

if __name__ == "__main__":
    app.run(debug=True)
