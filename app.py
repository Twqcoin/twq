import time
import threading
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# إعدادات قاعدة البيانات (SQLite في هذا المثال)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mining_state.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# تعريف جدول حالة التعدين
class MiningState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(100), nullable=False)

# وظيفة المهام في الخلفية
def background_task():
    while True:
        with app.app_context():
            try:
                print("Starting background task cycle...")
                # تحديث حالة التعدين في قاعدة البيانات
                state = MiningState.query.first()
                if state:
                    state.status = "Mining in progress"
                    print(f"Updated existing state: {state.status}")
                else:
                    state = MiningState(status="Mining in progress")
                    db.session.add(state)
                    print("Added new state: Mining in progress")
                db.session.commit()
                print("Database commit successful.")
            except Exception as e:
                print(f"Error: {e}")
        time.sleep(60)  # يتكرر كل دقيقة

# تشغيل المهام في الخلفية باستخدام threading
def run_background_task():
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    with app.app_context():
        state = MiningState.query.first()
        status = state.status if state else "No mining task started yet."
        print(f"Rendering home page with status: {status}")
        return render_template('index.html', status=status)

if __name__ == '__main__':
    # إنشاء قاعدة البيانات (إذا لم تكن موجودة)
    with app.app_context():
        db.create_all()

    run_background_task()  # بدء المهام في الخلفية
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)  # تم إغلاق القوس بشكل صحيح
