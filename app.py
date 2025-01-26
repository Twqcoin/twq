from flask import Flask
from celery import Celery
import os  # لاستخدام المتغيرات البيئية
import requests  # لاستيراد المكتبة بشكل عام

# تهيئة Flask
app = Flask(__name__)

# تعيين عنوان Redis من المتغيرات البيئية
app.config['CELERY_BROKER_URL'] = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# تهيئة Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# إنشاء Celery
celery = make_celery(app)

# مثال على مهمة Celery
@celery.task
def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')  # استرداد رمز البوت من المتغيرات البيئية
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')  # استرداد معرف الدردشة من المتغيرات البيئية
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message: {e}")

# واجهة API لاختبار Celery
@app.route('/send_message')
def send_message():
    send_telegram_message.delay("Hello from Celery!")
    return "Message sent to Telegram in the background!"

# مسار الصفحة الرئيسية
@app.route('/')
def home():
    return """
    <h1>Welcome to Flask with Celery!</h1>
    <p>Use the following endpoints to interact with the app:</p>
    <ul>
        <li><strong>/send_message</strong>: Sends a test message to Telegram.</li>
    </ul>
    """

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
