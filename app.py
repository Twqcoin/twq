from flask import Flask, render_template

# إنشاء تطبيق Flask
app = Flask(__name__)

# تعريف مسار الصفحة الرئيسية
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
