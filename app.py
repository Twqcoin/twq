from flask import Flask, render_template, request

# إنشاء تطبيق Flask
app = Flask(__name__)

# تحديد المسار الرئيسي (الرابط /)
@app.route('/')
def index():
    # عرض ملف index.html
    return render_template('index.html')

# إضافة مسار جديد لمعالجة بيانات التحليل (Analytics)
@app.route('/analytics', methods=['GET'])
def analytics():
    # استخراج الـ Token من الرابط
    token = request.args.get('token')
    
    # هنا يمكنك معالجة الـ token كما تحتاج (مثل تخزينه في قاعدة بيانات أو التحقق منه)
    print("Received token:", token)
    
    # الرد على الطلب
    return "Data received successfully!"

# تشغيل التطبيق في وضع التصحيح (debug) عندما يتم تشغيل السكربت مباشرة
if __name__ == '__main__':
    app.run(debug=True)
