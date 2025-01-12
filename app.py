from flask import Flask, render_template, jsonify
import psycopg2

app = Flask(__name__)

# إعداد الاتصال بقاعدة البيانات
connection = psycopg2.connect(
    host="your_host",
    database="game_db",  # اسم قاعدة البيانات التي تم إنشاؤها
    user="your_user",  # اسم المستخدم
    password="your_password"  # كلمة المرور
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
