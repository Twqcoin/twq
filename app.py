from flask import Flask, render_template, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from celery_config import make_celery

# تحميل المتغيرات من ملف .env
load_dotenv()

app = Flask(__name__)

# إعدادات Celery
app.config['CELERY_BROKER_URL'] = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# تهيئة Celery
celery = make_celery(app)

# إعداد الاتصال بقاعدة البيانات
connection = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    database=os.getenv("DB_NAME", "your_database_name"),
    user=os.getenv("DB_USER", "glqtsql"),
    password=os.getenv("DB_PASSWORD", "ciT4aeXYlbiqjhp"),
    port=os.getenv("DB_PORT", 5432)
)

cursor = connection.cursor()

@app.route("/players", methods=["GET"])
def get_players():
    cursor.execute("SELECT * FROM players;")
    players = cursor.fetchall()
    players_list = [{"id": player[0], "name": player[1]} for player in players]
    return jsonify(players_list)

@app.route("/")
def index():
    return render_template("index.html")

@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()

if __name__ == "__main__":
    app.run(debug=True)
