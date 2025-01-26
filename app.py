from flask import Flask
from celery import Celery

# تهيئة Flask
app = Flask(__name__)

# تهيئة Celery
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery

# تعيين المتغيرات البيئية
app.config['CELERY_BROKER_URL'] = 'redis://red-cu23f1tsvqrc73f22svg:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://red-cu23f1tsvqrc73f22svg:6379'

# إنشاء Celery
celery = make_celery(app)

# مثال على مهمة Celery
@celery.task
def send_telegram_message(message):
    import requests
    bot_token = app.config['TELEGRAM_BOT_TOKEN']
    chat_id = app.config['TELEGRAM_CHAT_ID']
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    requests.post(url, json=payload)

# واجهة API لاختبار Celery
@app.route('/send_message')
def send_message():
    send_telegram_message.delay("Hello from Celery!")
    return "Message sent to Telegram in the background!"

# تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)
