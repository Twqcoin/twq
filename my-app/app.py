from flask import Flask, request, jsonify
from celery import Celery
import time
import os

app = Flask(__name__)

# إعدادات Celery مع Redis كـ broker (تأكد من استخدام URL الخاص بـ Redis)
app.config['CELERY_BROKER_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # يمكنك استبدالها بـ URL الخاص بـ Redis Cloud
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# تخزين حالة التعدين للمستخدمين
mining_status = {}

# مهمة التعدين في worker منفصل
@celery.task
def start_mining_task(user_id):
    # محاكاة عملية التعدين
    mining_status[user_id] = {"status": "Mining", "elapsed_time": 0}
    for i in range(10):
        time.sleep(60)  # محاكاة التعدين لمدة 10 دقائق
        mining_status[user_id]["elapsed_time"] = i + 1
    mining_status[user_id]["status"] = "Completed"
    return f"Mining completed for user {user_id}"

@app.route('/start_mining', methods=['POST'])
def start_mining():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400
    
    # إرسال المهمة إلى worker في الخلفية
    task = start_mining_task.apply_async(args=[user_id])
    
    return jsonify({"status": "Mining started", "task_id": task.id})

@app.route('/mining_status/<user_id>', methods=['GET'])
def mining_status_route(user_id):
    # إرجاع حالة التعدين للمستخدم
    status = mining_status.get(user_id, {"status": "Not Started", "elapsed_time": 0})
    return jsonify(status)

if __name__ == "__main__":
    app.run(debug=True)
