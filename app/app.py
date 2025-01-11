from flask import Flask, render_template
from celery import Celery

app = Flask(__name__)

# إعدادات Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # إذا كنت تستخدم Redis محليًا أو عنوان Redis خارجي
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'  # نفس الشيء

# استيراد ملف celery_worker
from celery_worker import celery

@app.route('/')
def home():
    return render_template('index.html')  # إرجاع صفحة HTML

if __name__ == '__main__':
    app.run(debug=True)
