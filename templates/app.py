from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # قم بإنشاء هذا الملف داخل مجلد templates

if __name__ == "__main__":
    app.run(debug=True)
