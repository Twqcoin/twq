import time
import threading
from flask import Flask, render_template

app = Flask(__name__)

# وظيفة المهام في الخلفية
def background_task():
    while True:
        print("Running background task...")
        time.sleep(60)  # يتكرر كل دقيقة

# تشغيل المهام في الخلفية باستخدام threading
def run_background_task():
    thread = threading.Thread(target=background_task)
    thread.daemon = True
    thread.start()

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    run_background_task()  # بدء المهام في الخلفية
    app.run(host='0.0.0.0', port=5000)
