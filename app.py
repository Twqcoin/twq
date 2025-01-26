from flask import Flask
from routes import bp  # استيراد نقاط النهاية من routes.py

# إنشاء تطبيق Flask
app = Flask(__name__)

# تهيئة الإعدادات
app.config.from_object('config.Config')

# تسجيل نقاط النهاية (Routes)
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)
