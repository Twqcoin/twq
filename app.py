from flask import Flask, render_template

# إنشاء تطبيق Flask
app = Flask(__name__)

# تحديد المسار الرئيسي (الرابط /)
@app.route('/')
def index():
    # عرض ملف index.html
    return render_template('index.html')

# تشغيل التطبيق في وضع التصحيح (debug) عندما يتم تشغيل السكربت مباشرة
if __name__ == '__main__':
    app.run(debug=True)
