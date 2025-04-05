from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قاعدة بيانات أولية تحتوي على لاعب افتراضي
players_db = {
    1: {
        "id": 1,
        "name": "لاعب افتراضي",
        "imageUrl": "https://example.com/avatar.jpg",
        "points": 5000,
        "lastUpdated": datetime.now().isoformat()
    }
}

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

        player_data = players_db[player_id]
        
        # ضمان وجود جميع الحقول المطلوبة
        response_data = {
            "id": player_data["id"],
            "name": player_data.get("name", ""),
            "imageUrl": player_data.get("imageUrl", ""),
            "points": player_data.get("points", 0),
            "lastUpdated": player_data.get("lastUpdated", "")
        }

        return jsonify({
            "status": "success",
            "message": "",
            "data": response_data
        }), 200

    except Exception as e:
        logger.error(f"خطأ في الخادم: {str(e)}", exc_info=True)
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
        logger.error(f"خطأ في السحب: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": "حدث خطأ أثناء السحب",
            "data": None
        }), 500

def _build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
