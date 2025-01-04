from flask import Flask, render_template
import os

app = Flask(__name__)  # بدون static_folder

@app.route('/')
def index():
    return render_template('index.html')  # تأكد أن index.html في مجلد templates

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # الحصول على المنفذ من المتغيرات البيئية
    app.run(host="0.0.0.0", port=port)  # 
