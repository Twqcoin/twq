from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# قاعدة بيانات مؤقتة لتخزين بيانات اللاعبين
players_db = {}

@app.route('/api/player', methods=['POST'])
def handle_player():
    try:
        data = request.json
        
        # التحقق من البيانات المطلوبة
        if not all(key in data for key in ['id', 'name', 'imageUrl']):
            return jsonify({
                "status": "error",
                "message": "بيانات ناقصة. يرجى إرسال id و name و imageUrl"
            }), 400
        
        # تخزين/تحديث بيانات اللاعب
        players_db[data['id']] = {
            "name": data['name'],
            "imageUrl": data['imageUrl'],
            "points": data.get('points', 0),
            "lastUpdated": datetime.now().isoformat()
        }
        
        return jsonify({
            "status": "success",
            "message": "تم حفظ بيانات اللاعب",
            "data": players_db[data['id']]
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
    
    # تحديث النقاط
    players_db[player_id]['points'] = 0
    players_db[player_id]['lastUpdated'] = datetime.now().isoformat()
    
    return jsonify({
        "status": "success",
        "message": "تمت عملية السحب بنجاح",
        "data": players_db[player_id]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
