from flask import Flask

# إنشاء تطبيق Flask
app = Flask(__name__)

# تهيئة الإعدادات
app.config.from_object('config.Config')

# استيراد نقاط النهاية (Routes)
from app import routes
