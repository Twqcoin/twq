from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    # استلام البيانات من Unity
    data = request.get_json()
    print(f"Received data: {data}")
    
    # تأكد من أن البيانات تحتوي على 'from' و 'id' و 'first_name'
    if 'from' in data and 'id' in data['from'] and 'first_name' in data['from']:
        player_info = data['from']
        return jsonify({
            "player_data": {
                "name": player_info['first_name'],
                "photo_url": "https://example.com/avatar.jpg"  # يمكن تغيير الرابط لصورة فعلية
            }
        }), 200
    else:
        return jsonify({"error": "Invalid data format"}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
