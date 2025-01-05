import time
import threading
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

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
        # استخدام جلسة منفصلة آمنة
        with app.app_context():
            try:
                # تحديث حالة التعدين في قاعدة البيانات
                state = MiningState.query.first()
                if state:
                    state.status = "Mining in progress"
                else:
                    state = MiningState(status="Mining in progress")
                    db.session.add(state)
                db.session.commit()
                print("Running background task...")
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
    # عرض حالة التعدين من قاعدة البيانات
    with app.app_context():
        state = MiningState.query.first()
        if state:
            return render_template('index.html', status=state.status)
        else:
            return render_template('index.html', status="No mining task started yet.")

if __name__ == '__main__':
    # إنشاء قاعدة البيانات (إذا لم تكن موجودة)
    with app.app_context():
        db.create_all()

    run_background_task()  # بدء المهام في الخلفية
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)  # تم إغلاق القوس بشكل صحيح
إغلاق القوس بشكل صحيح
