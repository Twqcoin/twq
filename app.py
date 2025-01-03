from flask import Flask, render_template

app = Flask(name)

@app.route('/')
def home():
    return render_template('index.html')  # تقديم index.html

if __name__ == "__main__":
    app.run(debug=True)
