from flask import Flask, request, jsonify
from datetime import datetime
from flask_cors import CORS
import json
import signal
import sys
import logging
from threading import Lock
import atexit

# تهيئة التطبيق
app = Flask(__name__)
CORS(app)  # تمكين CORS للاتصال من Unity

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# قاعدة بيانات اللاعبين مع نظام قفل للخيوط المتعددة
players_db = {}
db_lock = Lock()

# ملف حفظ البيانات
DATA_FILE = 'players_data.json'

def save_data():
    """حفظ البيانات إلى ملف"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(players_db, f)
        logger.info("تم حفظ بيانات اللاعبين بنجاح")
    except Exception as e:
        logger.error(f"خطأ أثناء حفظ البيانات: {e}")

def load_data():
    """تحميل البيانات من ملف"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            # تحويل الـ string keys إلى integer
            return {int(k): v for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل البيانات: {e}")
        return {}

def handle_shutdown(signum=None, frame=None):
    """معالجة إشارات الإيقاف"""
    logger.info("تلقي إشارة إيقاف... حفظ البيانات قبل الخروج")
    save_data()
    sys.exit(0)

# تسجيل معالجات الإيقاف
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)
atexit.register(handle_shutdown)

# تحميل البيانات عند البدء
players_db = load_data()

@app.route('/api/player', methods=['POST'])
def handle_player():
    """معالجة إنشاء/تحديث اللاعب"""
    try:
        data = request.json
        
        # التحقق من البيانات المطلوبة
        if not data or 'id' not in data:
            return jsonify({
                "status": "error",
                "message": "معرف اللاعب مطلوب"
            }), 400
            
        player_id = data['id']
        
        with db_lock:
            if player_id in players_db:
                # تحديث البيانات الموجودة
                players_db[player_id].update({
                    "name": data.get('name', players_db[player_id]['name']),
                    "imageUrl": data.get('imageUrl', players_db[player_id]['imageUrl']),
                    "points": data.get('points', players_db[player_id]['points']),
                    "lastUpdated": datetime.now().isoformat()
                })
                message = "تم تحديث بيانات اللاعب"
            else:
                # إنشاء لاعب جديد
                players_db[player_id] = {
                    "id": player_id,
                    "name": data.get('name', f"Player_{player_id}"),
                    "imageUrl": data.get('imageUrl', "https://example.com/default_avatar.jpg"),
                    "points": data.get('points', 0),
                    "lastUpdated": datetime.now().isoformat()
                }
                message = "تم إنشاء لاعب جديد"
            
            # حفظ البيانات بعد التعديل
            save_data()
        
        return jsonify({
            "status": "success",
            "message": message,
            "data": players_db[player_id]
        })
        
    except Exception as e:
        logger.error(f"خطأ في معالجة اللاعب: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "حدث خطأ داخلي في الخادم"
        }), 500

@app.route('/api/player/<int:player_id>', methods=['GET'])
def get_player(player_id):
    """استرجاع بيانات اللاعب"""
    try:
        with db_lock:
            if player_id not in players_db:
                return jsonify({
                    "status": "error",
                    "message": "اللاعب غير موجود"
                }), 404
            
            return jsonify({
                "status": "success",
                "data": players_db[player_id]
            })
    except Exception as e:
        logger.error(f"خطأ في استرجاع بيانات اللاعب: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "حدث خطأ داخلي في الخادم"
        }), 500

@app.route('/api/player/<int:player_id>/withdraw', methods=['POST'])
def handle_withdraw(player_id):
    """معالجة طلب سحب النقاط"""
    try:
        with db_lock:
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
            
            # حفظ البيانات بعد التعديل
            save_data()
            
            return jsonify({
                "status": "success",
                "message": "تمت عملية السحب بنجاح",
                "data": players_db[player_id]
            })
    except Exception as e:
        logger.error(f"خطأ في معالجة السحب: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "حدث خطأ داخلي في الخادم"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """نقطة فحص صحة الخادم"""
    return jsonify({
        "status": "running",
        "players_count": len(players_db),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    try:
        logger.info("بدء تشغيل الخادم...")
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        logger.error(f"خطأ فادح في الخادم: {e}")
        handle_shutdown()
