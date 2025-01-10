from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_status.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج قاعدة البيانات لحالة التعدين
class MiningStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False)  # الوقت المنقضي بالدقائق
    start_time = db.Column(db.DateTime, nullable=True)  # وقت بدء التعدين

# إنشاء الجداول عند أول طلب
@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

# وظيفة لتحديث حالة التعدين لجميع اللاعبين
def update_all_mining_statuses():
    players = MiningStatus.query.all()
    for player in players:
        if player.status == "Mining" and player.start_time:
            now = datetime.now()
            delta = (now - player.start_time).total_seconds() / 60.0  # الفرق بالدقائق
            player.elapsed_time += delta
            player.start_time = now  # إعادة تعيين وقت البدء
    db.session.commit()

# جدولة الوظيفة
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_all_mining_statuses, trigger="interval", minutes=1)
scheduler.start()

# تأكد من إيقاف الجدول عند إيقاف التطبيق
atexit.register(lambda: scheduler.shutdown())

# صفحة البداية
@app.route('/')
def index():
    return render_template('index.html')

# جلب حالة التعدين
@app.route('/mining_status/<player_id>', methods=['GET'])
def get_mining_status(player_id):
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        # إذا كان التعدين نشطًا، حساب الوقت المنقضي منذ آخر تحديث
        if player.status == "Mining" and player.start_time:
            now = datetime.now()
            delta = (now - player.start_time).total_seconds() / 60.0  # الفرق بالدقائق
            return jsonify({"status": player.status, "elapsed_time": player.elapsed_time + delta})
        return jsonify({"status": player.status, "elapsed_time": player.elapsed_time})
    else:
        return jsonify({"status": "Not started", "elapsed_time": 0.0})

# بدء التعدين
@app.route('/start_mining/<player_id>', methods=['POST'])
def start_mining(player_id):
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        player.status = "Mining"
        player.start_time = datetime.now()  # تحديث وقت البدء
    else:
        player = MiningStatus(player_id=player_id, status="Mining", elapsed_time=0.0, start_time=datetime.now())
        db.session.add(player)

    db.session.commit()
    return jsonify({"status": "Mining started", "elapsed_time": player.elapsed_time})

# تحديث حالة التعدين
@app.route('/update_mining/<player_id>', methods=['POST'])
def update_mining(player_id):
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        if player.start_time:
            now = datetime.now()
            delta = (now - player.start_time).total_seconds() / 60.0  # الفرق بالدقائق
            player.elapsed_time += delta
            player.start_time = now  # إعادة تعيين وقت البدء
        db.session.commit()
        return jsonify({"status": player.status, "elapsed_time": player.elapsed_time})
    else:
        return jsonify({"status": "Not found", "elapsed_time": 0.0})

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
