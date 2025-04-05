import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from urllib.parse import urlparse
import uuid
from threading import Timer
import requests
from functools import wraps

# تهيئة التطبيق
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# تهيئة قاعدة البيانات البسيطة
class GameDatabase:
    def __init__(self):
        self.players = {}
        self.connections = {}
        
    def add_player(self, player_id, data):
        self.players[player_id] = data
        
    def get_player(self, player_id):
        return self.players.get(player_id)
        
    def add_connection(self, conn_id, data):
        self.connections[conn_id] = data
        
    def get_connection(self, conn_id):
        return self.connections.get(conn_id)

db = GameDatabase()

# متغيرات البيئة
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-webhook-url.com")
API_KEY = os.environ.get("API_KEY", "default-secret-key")

# ديكورات المساعدة
def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-KEY') != API_KEY:
            return jsonify({"status": "error", "message": "غير مصرح به"}), 401
        return view_function(*args, **kwargs)
    return decorated_function

def validate_image_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def cleanup_connection(connection_id):
    if db.get_connection(connection_id):
        del db.connections[connection_id]
        logger.info(f"تم تنظيف اتصال: {connection_id}")

def send_to_webhook(data):
    try:
        response = requests.post(
            WEBHOOK_URL, 
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        response.raise_for_status()
        logger.info("تم إرسال البيانات إلى Webhook بنجاح")
    except Exception as e:
        logger.error(f"خطأ في إرسال Webhook: {str(e)}")

# مسارات API
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/player', methods=['GET'])
@require_api_key
def get_player():
    player_id = request.args.get('player_id')
    if not player_id:
        return jsonify({"status": "error", "message": "معرف اللاعب مطلوب"}), 400
        
    player = db.get_player(player_id)
    if not player:
        return jsonify({"status": "error", "message": "اللاعب غير موجود"}), 404
        
    return jsonify({
        "status": "success",
        "data": player,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/player/update', methods=['POST'])
@require_api_key
def update_player():
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['player_id', 'name']
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "بيانات ناقصة"}), 400
        
        # التحقق من صحة صورة اللاعب
        image_url = data.get('imageUrl', '')
        if image_url and not validate_image_url(image_url):
            image_url = "https://via.placeholder.com/300"
            logger.warning("تم استخدام صورة افتراضية")
        
        # إنشاء/تحديث بيانات اللاعب
        player_data = {
            "player_id": data['player_id'],
            "name": data['name'],
            "imageUrl": image_url,
            "lastUpdated": datetime.now().isoformat(),
            "points": data.get('points', 0)
        }
        
        db.add_player(data['player_id'], player_data)
        
        # إنشاء اتصال جديد إذا لزم الأمر
        if data.get('create_connection', False):
            connection_id = str(uuid.uuid4())
            db.add_connection(connection_id, {
                "player_id": data['player_id'],
                "status": "pending",
                "created_at": datetime.now().isoformat()
            })
            Timer(1800, cleanup_connection, [connection_id]).start()
            
        # إرسال تحديث إلى Webhook
        send_to_webhook(player_data)
        
        logger.info(f"تم تحديث لاعب: {data['player_id']}")
        
        return jsonify({
            "status": "success",
            "message": "تم تحديث بيانات اللاعب",
            "data": player_data
        })
        
    except Exception as e:
        logger.error(f"خطأ في تحديث اللاعب: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/connection/<connection_id>', methods=['GET', 'POST'])
@require_api_key
def handle_connection(connection_id):
    try:
        connection = db.get_connection(connection_id)
        if not connection:
            return jsonify({"status": "error", "message": "الاتصال غير موجود"}), 404
            
        if request.method == 'POST':
            data = request.get_json()
            connection.update({
                "status": data.get('status', connection['status']),
                "updated_at": datetime.now().isoformat()
            })
            logger.info(f"تم تحديث اتصال: {connection_id}")
            
        return jsonify({
            "status": "success",
            "data": connection
        })
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الاتصال: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# تشغيل الخادم
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    )
