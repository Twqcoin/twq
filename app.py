import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from urllib.parse import urlparse
import uuid
from threading import Timer

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تحميل المتغيرات البيئية من Render
SERVER_URL = os.environ.get("SERVER_URL", "https://your-server.com")
TON_CONNECT_ENDPOINT = os.environ.get("TON_CONNECT_ENDPOINT", "/ton/connect")
TON_STATUS_ENDPOINT = os.environ.get("TON_STATUS_ENDPOINT", "/ton/status")
TON_DEEP_LINK = os.environ.get("TON_DEEP_LINK", "tonconnect://connect")
MANIFEST_URL = os.environ.get("MANIFEST_URL", "https://your-site.com/tonconnect-manifest.json")

# تخزين بيانات اللاعب والاتصالات
player_data = {
    "name": "لاعب جديد",
    "imageUrl": "https://via.placeholder.com/300",
    "lastUpdated": None
}

active_connections = {}

def validate_image_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def cleanup_connection(connection_id):
    if connection_id in active_connections:
        del active_connections[connection_id]
        logger.info(f"🧹 تم تنظيف اتصال: {connection_id}")

@app.route('/api/player', methods=['GET'])
def get_player():
    logger.info(f"📥 طلب GET - اللاعب: {player_data['name']}")
    return jsonify({
        "status": "success",
        "data": player_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/update', methods=['POST'])
def update_player():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            raise ValueError("⚠️ يجب تقديم اسم اللاعب")
        
        image_url = data.get('imageUrl', '')
        if not validate_image_url(image_url):
            image_url = "https://via.placeholder.com/300"
            logger.warning("📷 تم استخدام صورة افتراضية")
        
        connection_id = data.get('connectionId', str(uuid.uuid4()))
        if connection_id:
            active_connections[connection_id] = {
                "status": "pending",
                "player_name": data['name'],
                "created_at": datetime.now()
            }
            Timer(1800, cleanup_connection, [connection_id]).start()
        
        player_data.update({
            "name": data['name'],
            "imageUrl": image_url,
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        logger.info(f"✅ تم التحديث - اللاعب: {player_data['name']} | اتصال: {connection_id}")
        
        return jsonify({
            "status": "success",
            "message": "تم تحديث البيانات وإنشاء الاتصال",
            "connectionId": connection_id,
            "deepLink": f"tg://wallet?startapp={connection_id}",
            "data": player_data
        })
        
    except Exception as e:
        logger.error(f"❌ خطأ في التحديث: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

@app.route('/api/connection/<connection_id>', methods=['GET', 'POST'])
def handle_connection(connection_id):
    try:
        if request.method == 'POST':
            data = request.get_json()
            if connection_id in active_connections:
                active_connections[connection_id].update({
                    "status": data.get('status', 'pending'),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                logger.info(f"🔄 تم تحديث الاتصال: {connection_id}")
                return jsonify({
                    "status": "success",
                    "message": "تم تحديث حالة الاتصال",
                    "data": active_connections[connection_id]
                })
            else:
                raise ValueError("الاتصال غير موجود")
        
        if connection_id in active_connections:
            return jsonify({
                "status": "success",
                "connection": active_connections[connection_id]
            })
        else:
            return jsonify({
                "status": "error",
                "message": "الاتصال غير موجود"
            }), 404

    except Exception as e:
        logger.error(f"❌ خطأ في التعامل مع الاتصال: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

# ✅ تشغيل الخادم
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
