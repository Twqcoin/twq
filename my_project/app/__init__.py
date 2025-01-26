from flask import Flask

# إنشاء نسخة Flask
app = Flask(__name__)

# تهيئة الإعدادات
app.config.from_object('config.Config')

# تسجيل نقاط النهاية (Routes)
from app import routes
