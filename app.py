from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

player_data = {
    "name": "لاعب جديد",
    "imageUrl": "https://via.placeholder.com/300",
    "lastUpdated": None
}

def validate_image_url(url):
    try:
        result = urlparse(url)
        if not all([result.scheme in ['http', 'https'], result.netloc]):
            return False
        return True
    except:
        return False

@app.route('/api/player', methods=['GET'])
def get_player():
    logger.info(f"تم استلام طلب GET - الإسم: {player_data['name']}")
    return jsonify({
        "status": "success",
        "data": player_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/update', methods=['POST'])
def update_player():
    global player_data
    
    try:
        data = request.get_json()
        
        # التحقق من البيانات الأساسية
        if not data or 'name' not in data:
            raise ValueError("يجب تقديم اسم اللاعب")
        
        # معالجة صورة اللاعب
        image_url = data.get('imageUrl', '')
        if not validate_image_url(image_url):
            image_url = "https://via.placeholder.com/300"
            logger.warning("تم استخدام صورة افتراضية بسبب رابط غير صالح")
        
        # تحديث البيانات
        player_data = {
            "name": data['name'],
            "imageUrl": image_url,
            "lastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"تم التحديث - الإسم: {player_data['name']} | الصورة: {player_data['imageUrl']}")
        return jsonify({
            "status": "success",
            "message": "تم تحديث بيانات اللاعب",
            "data": player_data
        })
        
    except Exception as e:
        logger.error(f"خطأ في التحديث: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
