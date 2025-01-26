from flask import Flask

# إنشاء تطبيق Flask
app = Flask(__name__)

# تهيئة الإعدادات
app.config.from_object('config.Config')

# استيراد وتسجيل نقاط النهاية (Routes)
from app.routes import bp
app.register_blueprint(bp)
