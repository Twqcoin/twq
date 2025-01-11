from flask import Flask, render_template
from celery_worker import make_celery  # استيراد make_celery بدلاً من celery مباشرة

app = Flask(__name__)

# إعدادات Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # أو عنوان Redis الخاص بك
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# تهيئة Celery مع Flask بعد تهيئة التطبيق
celery = make_celery(app)

@app.route('/')
def home():
    return render_template('index.html')  # إرجاع صفحة HTML

if __name__ == '__main__':
    app.run(debug=True)
