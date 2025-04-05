from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قاعدة بيانات اللاعبين
players_db = {
    1: {
        "id": 1,
        "name": "لاعب افتراضي",
        "imageUrl": "https://example.com/avatar.jpg",
        "points": 5000,
        "lastUpdated": datetime.now().isoformat()
    }
}

@app.route('/api/player', methods=['POST', 'OPTIONS'])
def handle_player():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        logger.info(f"بيانات الواردة: {data}")
        
        if not data or 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "معرف اللاعب مطلوب",
                "data": None
            }), 400
            
        player_id = data['id']
        
        if player_id in players_db:
            return jsonify({
                "status": "error",
                "message": "اللاعب موجود بالفعل",
                "data": None
            }), 409
            
        players_db[player_id] = {
            "id": player_id,
            "name": data.get('name', f"Player_{player_id}"),
            "imageUrl": data.get('imageUrl', ""),
            "points": data.get('points', 0),
            "lastUpdated": datetime.now().isoformat()
        }
        
        logger.info(f"تم إنشاء لاعب جديد: {players_db[player_id]}")
        
        return jsonify({
            "status": "success",
            "message": "تم إنشاء اللاعب بنجاح",
            "data": players_db[player_id]
        }), 201
        
    except Exception as e:
        logger.error(f"خطأ: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "حدث خطأ في الخادم",
            "data": None
        }), 500

@app.route('/api/player/<int:player_id>', methods=['GET', 'OPTIONS'])
def get_player(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if player_id not in players_db:
            return jsonify({
                "status": "error",
                "message": "اللاعب غير موجود",
                "data": None
            }), 404
        
        return jsonify({
            "status": "success",
            "message": "",
            "data": players_db[player_id]
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "حدث خطأ في الخادم",
            "data": None
        }), 500

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST', 'OPTIONS'])
def withdraw_points(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if player_id not in players_db:
            return jsonify({
                "status": "error",
                "message": "اللاعب غير موجود",
                "data": None
            }), 404
        
        if players_db[player_id]['points'] < 1000:
            return jsonify({
                "status": "error",
                "message": "النقاط غير كافية للسحب",
                "data": None
            }), 400
        
        players_db[player_id]['points'] -= 1000
        players_db[player_id]['lastUpdated'] = datetime.now().isoformat()
        
        return jsonify({
            "status": "success",
            "message": "تم السحب بنجاح",
            "data": {
                "newPoints": players_db[player_id]['points']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"خطأ: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "حدث خطأ في الخادم",
            "data": None
        }), 500

def _build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
