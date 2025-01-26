import os
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

class Config:
    # إعدادات Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_secret_key')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'

    # إعدادات قاعدة البيانات
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_PORT = os.getenv('DB_PORT', '5432')

    # إعدادات Celery
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # إعدادات Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
