from celery import Celery
import time

# تكوين Celery مع Redis
app = Celery('app', broker='redis://localhost:6379/0')  # تأكد من تعديل عنوان Redis إذا كنت تستخدم Redis Cloud أو غيره

# تعريف مهمة Celery (task)
@app.task
def long_running_task():
    print("Starting long-running task...")
    time.sleep(10)  # محاكاة مهمة طويلة
    print("Task completed!")
    return "Task completed"
