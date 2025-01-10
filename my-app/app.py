from flask import Flask, request, jsonify
from celery import Celery
import time

app = Flask(__name__)

# إعدادات Celery مع Redis كـ broker
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'  # تغيير إذا كنت تستخدم Redis Cloud أو خادم بعيد
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# مهمة التعدين في worker منفصل
@celery.task
def start_mining_task(user_id):
    # هنا يتم محاكاة عملية التعدين
    time.sleep(10)  # التعدين يستغرق وقتًا
    # تحديث قاعدة البيانات هنا (أو إتمام عملية أخرى)
    return f"Mining started for user {user_id}"

@app.route('/start_mining', methods=['POST'])
def start_mining():
    user_id = request.json.get('user_id')
    # إرسال المهمة إلى worker في الخلفية
    task = start_mining_task.apply_async(args=[user_id])
    return jsonify({"status": "Mining started", "task_id": task.id})

if __name__ == "__main__":
    app.run(debug=True)
