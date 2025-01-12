from flask import Flask, render_template, jsonify
import psycopg2
import os
from dotenv import load_dotenv
from celery_worker import make_celery  # تأكد من استيراد make_celery من celery_worker

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
    database=os.getenv("DB_NAME", "game_db"),
    user=os.getenv("DB_USER", "your_user"),
    password=os.getenv("DB_PASSWORD", "your_password")
)

# إنشاء كائن Cursor للتفاعل مع قاعدة البيانات
cursor = connection.cursor()

# دالة لعرض اللاعبين
@app.route("/players", methods=["GET"])
def get_players():
    cursor.execute("SELECT * FROM players;")
    players = cursor.fetchall()
    players_list = [{"id": player[0], "name": player[1]} for player in players]
    return jsonify(players_list)

# صفحة الـ index لعرض اللاعبين
@app.route("/")
def index():
    return render_template("index.html")

# إغلاق الاتصال عند الخروج
@app.teardown_appcontext
def close_connection(exception):
    cursor.close()
    connection.close()

if __name__ == "__main__":
    app.run(debug=True)
