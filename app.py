from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

players_db = {}

@app.route('/')
def home():
    return "🚀 خادم اللعبة يعمل بنجاح!", 200

@app.route('/api/player', methods=['POST'])
def add_player():
    try:
        data = request.json
        
        if not data.get('id'):
            return jsonify({"status": "error", "message": "ID مطلوب"}), 400
            
        player_id = data['id']
        
        players_db[player_id] = {
            "id": player_id,
            "name": data.get('name', f"Player_{player_id}"),  # تم التصحيح هنا
            "imageUrl": data.get('imageUrl', "https://example.com/avatar.jpg"),
            "points": data.get('points', 0),
            "lastUpdated": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "data": players_db[player_id]
        })
        
    except Exception as e:
        logger.error(f"خطأ: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ"}), 500

@app.route('/api/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    if player_id not in players_db:
        return jsonify({"status": "error", "message": "لاعب غير موجود"}), 404
        
    return jsonify({"status": "success", "data": players_db[player_id]})

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST'])
def withdraw_points(player_id):
    if player_id not in players_db:
        return jsonify({"status": "error", "message": "لاعب غير موجود"}), 404
        
    if players_db[player_id]['points'] < 1000:
        return jsonify({"status": "error", "message": "نقاط غير كافية"}), 400
        
    players_db[player_id]['points'] = 0
    return jsonify({"status": "success", "message": "تم السحب!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
