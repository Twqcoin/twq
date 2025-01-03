from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('Build', 'index.html')

@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory('Build', path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=os.environ.get("PORT", 5000))
