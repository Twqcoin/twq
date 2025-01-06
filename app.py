from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_status.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج قاعدة البيانات لحفظ حالة التعدين
class MiningStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<MiningStatus {self.player_id}: {self.status}>"

# إنشاء الجداول في قاعدة البيانات
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mining_status/<player_id>', methods=['GET'])
def mining_status_route(player_id):
    # الحصول على حالة التعدين من قاعدة البيانات
    mining_status = MiningStatus.query.filter_by(player_id=player_id).first()
    
    if mining_status:
        return jsonify({
            "status": mining_status.status,
            "elapsed_time": mining_status.elapsed_time
        })
    else:
        return jsonify({"error": "Mining status not found"}), 404

@app.route('/start_mining/<player_id>', methods=['POST'])
def start_mining(player_id):
    # بدء عملية التعدين (مثال بسيط)
    new_status = MiningStatus(player_id=player_id, status="Mining in progress", elapsed_time=0.0)
    db.session.add(new_status)
    db.session.commit()
    return jsonify({"message": "Mining started for player " + player_id})

@app.route('/update_mining_status/<player_id>', methods=['POST'])
def update_mining_status(player_id):
    mining_status = MiningStatus.query.filter_by(player_id=player_id).first()
    
    if mining_status:
        mining_status.status = "Mining completed"
        mining_status.elapsed_time = 123.45  # يجب تحديث الوقت بناءً على المنطق الفعلي
        db.session.commit()
        return jsonify({"message": "Mining status updated"})
    else:
        return jsonify({"error": "Mining status not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
