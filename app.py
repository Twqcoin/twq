import logging
from flask import Flask, render_template, jsonify
import time
import threading
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات قاعدة البيانات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_state.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# إعدادات السجل
logging.basicConfig(level=logging.DEBUG)

# تعريف جدول حالة التعدين
class MiningState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.Float, nullable=False)
    elapsed_time = db.Column(db.Float, nullable=True)  # إضافة العمود لاحتساب الوقت المستغرق

# وظيفة المهام في الخلفية
def background_task():
    while True:
        with app.app_context():
            try:
                state = MiningState.query.first()
                if state:
                    elapsed_time = time.time() - state.start_time
                    state.status = "Mining in progress"
                    state.elapsed_time = elapsed_time  # تحديث الوقت المستغرق
                    logging.debug(f"Mining in progress... Elapsed time: {elapsed_time:.2f} seconds")
                else:
                    state = MiningState(status="Mining in progress", start_time=time.time())
                    db.session.add(state)
                    logging.debug("New mining session started.")
                db.session.commit()
                logging.debug(f"Background task running... Status: {state.status}, Elapsed Time: {state.elapsed_time:.2f} seconds")
            except Exception as e:
                logging.error(f"Error: {e}")
        time.sleep(60)

# تشغيل المهام في الخلفية
def run_background_task():
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_mining', methods=['POST'])
def start_mining():
    with app.app_context():
        state = MiningState.query.first()
        if state:
            state.status = "Mining started"
            state.start_time = time.time()
            state.elapsed_time = 0  # إعادة تعيين الوقت المستغرق إلى صفر عند بدء التعدين
        else:
            state = MiningState(status="Mining started", start_time=time.time(), elapsed_time=0)
            db.session.add(state)
        db.session.commit()
        logging.info("Mining started!")
    return jsonify({"status": "Mining started"}), 200

@app.route('/mining_status/<player_id>', methods=['GET'])
def mining_status(player_id):
    with app.app_context():
        state = MiningState.query.first()
        if state:
            elapsed_time = time.time() - state.start_time
            logging.debug(f"Mining status fetched: {state.status}, Elapsed time: {elapsed_time:.2f} seconds")
            return jsonify({"status": state.status, "elapsed_time": elapsed_time}), 200
        else:
            logging.debug("No mining task started yet.")
            return jsonify({"status": "No mining task started", "elapsed_time": 0}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # إنشاء قاعدة البيانات إذا لم تكن موجودة
    run_background_task()
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
