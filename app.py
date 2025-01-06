# app.py
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_status.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج قاعدة البيانات لحالة التعدين
class MiningStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False)

# إنشاء الجداول عند أول طلب
@app.before_request
def create_tables():
    # يتم التحقق إذا كانت الجداول موجودة، وإذا لم تكن سيتم إنشاؤها
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mining_status/<player_id>', methods=['GET'])
def get_mining_status(player_id):
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        return jsonify({"status": player.status, "elapsed_time": player.elapsed_time})
    else:
        return jsonify({"status": "Not started", "elapsed_time": 0.0})

@app.route('/start_mining/<player_id>', methods=['POST'])
def start_mining(player_id):
    # بدء التعدين للاعب
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        player.status = "Mining"
        player.elapsed_time = 0.0
    else:
        player = MiningStatus(player_id=player_id, status="Mining", elapsed_time=0.0)
        db.session.add(player)

    db.session.commit()
    return jsonify({"status": "Mining started", "elapsed_time": player.elapsed_time})

@app.route('/update_mining/<player_id>', methods=['POST'])
def update_mining(player_id):
    # تحديث الوقت المنقضي للتعدين
    player = MiningStatus.query.filter_by(player_id=player_id).first()
    if player:
        player.elapsed_time += 0.1  # زيادة الوقت المنقضي
        db.session.commit()
        return jsonify({"status": player.status, "elapsed_time": player.elapsed_time})
    else:
        return jsonify({"status": "Not found", "elapsed_time": 0.0})

if __name__ == '__main__':
    app.run(debug=True)
