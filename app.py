from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'HEAD'])
def home():
    return render_template('index.html')  # تأكد من أن الملف موجود في مجلد templates


if __name__ == "__main__":
    app.run(debug=True)
