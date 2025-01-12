from flask import Flask, render_template, jsonify
from celery_worker import make_celery
import time

app = Flask(__name__)

# إعدادات Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# تهيئة Celery
celery = make_celery(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_mining/<player_id>')
def start_mining(player_id):
    task = mining_task.apply_async(args=[player_id])  # بدء المهمة في الخلفية
    return jsonify({"task_id": task.id}), 202

@app.route('/mining_status/<task_id>')
def mining_status(task_id):
    task = mining_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        return jsonify({"status": "Mining is still running..."})
    elif task.state == 'SUCCESS':
        return jsonify({"status": "Mining complete!", "result": task.result})
    else:
        return jsonify({"status": "Mining failed or was aborted"})

# مهمة Celery للتعدين
@celery.task
def mining_task(player_id):
    # منطق التعدين الذي تريده هنا
    print(f"تعدين جاري لللاعب {player_id}")
    for i in range(10):  # محاكاة عملية التعدين
        time.sleep(1)
    return f"التعدين لللاعب {player_id} اكتمل!"
    
if __name__ == '__main__':
    app.run(debug=True)
