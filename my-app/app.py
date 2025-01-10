from flask import Flask, request, jsonify
import time
app = Flask(__name__)

@app.route('/start_mining', methods=['POST'])
def start_mining():
    user_id = request.json.get('user_id')
    # هنا يتم تحديث قاعدة البيانات بأن التعدين بدأ
    # تشغيل التعدين في Worker منفصل
    return jsonify({"status": "Mining started"})

if __name__ == "__main__":
    app.run(debug=True)
