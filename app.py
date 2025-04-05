from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

players_db = {}

@app.route('/api/player', methods=['POST', 'OPTIONS'])
def handle_player():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        logger.info(f"بيانات الواردة: {data}")
        
        if not data or 'id' not in data:
            return _corsify_response(jsonify({
                "status": "error",
                "message": "معرف اللاعب مطلوب"
            })), 400
            
        player_id = data['id']
        
        players_db[player_id] = {
            "id": player_id,
            "name": data.get('name', f"Player_{player_id}"),
            "imageUrl": data.get('imageUrl', "https://example.com/avatar.jpg"),
            "points": data.get('points', 0),
            "lastUpdated": datetime.now().isoformat()
        }
        
        logger.info(f"تم حفظ بيانات اللاعب: {players_db[player_id]}")
        
        return _corsify_response(jsonify({
            "status": "success",
            "data": players_db[player_id]
        }))
        
    except Exception as e:
        logger.error(f"خطأ: {str(e)}")
        return _corsify_response(jsonify({
            "status": "error",
            "message": "حدث خطأ في الخادم"
        })), 500

@app.route('/api/player/<int:player_id>', methods=['GET', 'OPTIONS'])
def get_player(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if player_id not in players_db:
        return _corsify_response(jsonify({
            "status": "error",
            "message": "اللاعب غير موجود"
        })), 404
    
    return _corsify_response(jsonify({
        "status": "success",
        "data": players_db[player_id]
    }))

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST', 'OPTIONS'])
def withdraw_points(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    if player_id not in players_db:
        return _corsify_response(jsonify({
            "status": "error",
            "message": "اللاعب غير موجود"
        })), 404
    
    if players_db[player_id]['points'] < 1000:
        return _corsify_response(jsonify({
            "status": "error",
            "message": "النقاط غير كافية للسحب"
        })), 400
    
    players_db[player_id]['points'] = 0
    return _corsify_response(jsonify({
        "status": "success",
        "message": "تم السحب بنجاح"
    }))

def _build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    return response

def _corsify_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
