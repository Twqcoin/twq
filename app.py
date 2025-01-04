from flask import Flask, render_template

# تحديد التطبيق وإنشاءه مع تحديد مكان القوالب في المجلد الحالي (المجلد الذي يحتوي على app.py و index.html)
app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    # عرض ملف index.html الموجود في نفس المجلد
    return render_template('index.html')

if __name__ == '__main__':
    # تشغيل الخادم
    app.run(debug=True)
