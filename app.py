from flask import Flask, render_template, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from celery_worker import make_celery  # Ensure make_celery is imported from celery_worker

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Celery configuration
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Initialize Celery
celery = make_celery(app)

# Database connection setup
connection = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "game_db"),
    user=os.getenv("DB_USER", "your_user"),
    password=os.getenv("DB_PASSWORD", "your_password")
)

# Create a cursor object to interact with the database
cursor = connection.cursor()

# Route to display players
@app.route("/players", methods=["GET"])
def get_players():
    cursor.execute("SELECT * FROM players;")
    players = cursor.fetchall()
    players_list = [{"id": player[0], "name": player[1]} for player in players]
    return jsonify(players_list)

# Index page route
@app.route("/")
def index():
    return render_template("index.html")

# Close the database connection when the app context ends
@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()

if __name__ == "__main__":
    app.run(debug=True)
