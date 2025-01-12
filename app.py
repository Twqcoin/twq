from flask import Flask, request, jsonify, render_template
import json
import base64

app = Flask(__name__)

@app.route('/')
def index():
    data_param = request.args.get('data')
    if data_param:
        try:
            # إضافة حشو إذا لزم الأمر
            missing_padding = len(data_param) % 4
            if missing_padding:
                data_param += '=' * (4 - missing_padding)

            # فك تشفير البيانات باستخدام Base64
            decoded_data = base64.urlsafe_b64decode(data_param)

            # التأكد من أن البيانات ليست فارغة
            if not decoded_data:
                raise ValueError("Decoded data is empty")

            # محاولة فك التشفير باستخدام UTF-8، وإذا فشلت يتم استخدام Latin-1
            try:
                decoded_str = decoded_data.decode('utf-8')
            except UnicodeDecodeError:
                decoded_str = decoded_data.decode('latin-1')

            # طباعة البيانات المفكوكة لفحصها
            print("Decoded string:", decoded_str)

            # محاولة تحميل البيانات إلى JSON
            try:
                player_data = json.loads(decoded_str)
            except json.JSONDecodeError as e:
                return f"Error decoding JSON: {e.msg}", 400

            # استخراج بيانات اللاعب
            player_name = player_data.get('name', 'Unknown Player')
            player_image = player_data.get('profile_pic', '')

            # تمرير البيانات إلى القالب لعرضها
            return render_template('index.html', player_name=player_name, player_image=player_image)

        except (ValueError, base64.binascii.Error) as e:
            return f"Error processing player data: {str(e)}", 400
    else:
        return "No player data provided", 400

if __name__ == '__main__':
    app.run(debug=True)
