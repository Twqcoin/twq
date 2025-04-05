from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # تمكين CORS للاتصال من Unity

players_db = {}

@app.route('/api/player', methods=['POST'])
def handle_player():
    try:
        data = request.json
        
        # إنشاء أو تحديث بيانات اللاعب
        if 'id' not in data:
            return jsonify({"status": "error", "message": "معرف اللاعب مطلوب"}), 400
            
        player_id = data['id']
        
        if player_id in players_db:
            # تحديث البيانات الموجودة
            players_db[player_id].update({
                "name": data.get('name', players_db[player_id]['name']),
                "imageUrl": data.get('imageUrl', players_db[player_id]['imageUrl']),
                "points": data.get('points', players_db[player_id]['points']),
                "lastUpdated": datetime.now().isoformat()
            })
        else:
            # إنشاء لاعب جديد
            players_db[player_id] = {
                "id": player_id,
                "name": data.get('name', f"Player_{player_id}"),
                "imageUrl": data.get('imageUrl', "https://example.com/default_avatar.jpg"),
                "points": data.get('points', 0),
                "lastUpdated": datetime.now().isoformat()
            }
        
        return jsonify({
            "status": "success",
            "message": "تم حفظ بيانات اللاعب",
            "data": players_db[player_id]
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"خطأ في الخادم: {str(e)}"
        }), 500

@app.route('/api/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    if player_id not in players_db:
        return jsonify({
            "status": "error",
            "message": "اللاعب غير موجود"
        }), 404
    
    return jsonify({
        "status": "success",
        "data": players_db[player_id]
    })

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST'])
def handle_withdraw(player_id):
    if player_id not in players_db:
        return jsonify({
            "status": "error",
            "message": "اللاعب غير موجود"
        }), 404
    
    if players_db[player_id]['points'] < 1000:
        return jsonify({
            "status": "error",
            "message": "النقاط غير كافية للسحب"
        }), 400
    
    # تسجيل عملية السحب
    players_db[player_id]['points'] = 0
    players_db[player_id]['lastUpdated'] = datetime.now().isoformat()
    
    return jsonify({
        "status": "success",
        "message": "تمت عملية السحب بنجاح",
        "data": players_db[player_id]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
