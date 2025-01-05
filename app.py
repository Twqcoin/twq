from flask import Flask, render_template, request
from celery import Celery
import time

app = Flask(__name__)

# إعداد Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# وظيفة التعدين كمهمة Celery
@celery.task
def mining_task():
    while True:
        # محاكاة عملية التعدين
        print("Mining in progress...")
        time.sleep(60)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start-mining', methods=['POST'])
def start_mining():
    mining_task.delay()  # تشغيل المهمة في الخلفية
    return "Mining started"

if __name__ == '__main__':
    app.run(debug=True)
