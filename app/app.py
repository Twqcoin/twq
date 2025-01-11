from flask import Flask, jsonify
from celery_worker import long_running_task  # استيراد المهمة

app = Flask(__name__)

@app.route('/start_task', methods=['GET'])
def start_task():
    task = long_running_task.apply_async()  # إرسال المهمة إلى Celery worker
    return jsonify({"status": "Task started", "task_id": task.id})

if __name__ == "__main__":
    app.run(debug=True)
