from flask import Flask, jsonify

# 1. إنشاء تطبيق Flask
app = Flask(__name__)

# 2. تعريف مسار بسيط للصفحة الرئيسية
@app.route('/')
def home():
    return jsonify({"message": "مرحبًا، هذا تطبيق Flask يعمل على Render!"})

# 3. تعريف مسار آخر كمثال
@app.route('/about')
def about():
    return jsonify({"message": "هذه صفحة حول التطبيق."})

# 4. تشغيل التطبيق (هذا الجزء غير مطلوب عند استخدام gunicorn)
if __name__ == '__main__':
    app.run(debug=True)
