# server.py

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Flask Server is running!"

@app.route('/player', methods=['POST'])
def receive_player():
    data = request.get_json()

    if not data:
        return jsonify({"status": "fail", "message": "No data received"}), 400

    print("\n📥 تم استلام بيانات اللاعب:")
    print(f"🆔 ID: {data.get('id')}")
    print(f"👤 Name: {data.get('name')}")
    print(f"🖼️ Photo URL: {data.get('photo')}")

    return jsonify({"status": "success", "message": "Player data received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
