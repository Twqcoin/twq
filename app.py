from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import logging
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# إعدادات CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', "*"),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قاعدة بيانات مؤقتة
players_db = {}

@app.route('/api/player', methods=['POST', 'OPTIONS'])
def handle_player():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")

        if not data or 'id' not in data:
            return _error_response("معرف اللاعب مطلوب", 400)

        player_id = data['id']
        
        if player_id in players_db:
            return _error_response("اللاعب موجود بالفعل", 409)
        
        # إنشاء لاعب جديد
        players_db[player_id] = {
            "id": player_id,
            "name": data.get('name', f"Player_{player_id}"),
            "imageUrl": data.get('imageUrl', ""),
            "points": data.get('points', 2000),
            "lastUpdated": datetime.now().isoformat()
        }

        logger.info(f"Player created: {players_db[player_id]}")
        return _success_response("تم إنشاء اللاعب بنجاح", players_db[player_id], 201)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return _error_response("حدث خطأ في الخادم", 500)

@app.route('/api/player/<int:player_id>', methods=['GET', 'OPTIONS'])
def get_player(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if player_id not in players_db:
            return _error_response("اللاعب غير موجود", 404)
        
        return _success_response("", players_db[player_id])

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return _error_response("حدث خطأ في الخادم", 500)

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST', 'OPTIONS'])
def withdraw_points(player_id):
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    
    try:
        if player_id not in players_db:
            return _error_response("اللاعب غير موجود", 404)
        
        if players_db[player_id]['points'] < 1000:
            return _error_response("النقاط غير كافية للسحب", 400)
        
        # عملية السحب
        players_db[player_id]['points'] -= 1000
        players_db[player_id]['lastUpdated'] = datetime.now().isoformat()
        
        return _success_response("تم السحب بنجاح", {
            "newPoints": players_db[player_id]['points']
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return _error_response("حدث خطأ في الخادم", 500)

# دوال مساعدة
def _build_cors_preflight_response():
    response = jsonify({"status": "success"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    return response

def _success_response(message, data=None, status_code=200):
    return jsonify({
        "status": "success",
        "message": message,
        "data": data
    }), status_code

def _error_response(message, status_code):
    return jsonify({
        "status": "error",
        "message": message,
        "data": None
    }), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
