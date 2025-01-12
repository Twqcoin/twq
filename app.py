from flask import request, jsonify
import json
import base64

@app.route('/')
def index():
    data_param = request.args.get('data')
    if data_param:
        try:
            decoded_data = base64.urlsafe_b64decode(data_param)
            player_data = json.loads(decoded_data)
            player_name = player_data.get('name', 'Unknown Player')
            player_image = player_data.get('profile_pic', '')

            # هنا يمكن تمرير البيانات إلى الواجهة لعرضها
            return render_template('index.html', player_name=player_name, player_image=player_image)
        except Exception as e:
            print(f"Error decoding data: {e}")
            return "Error processing player data", 400
    else:
        return "No player data provided", 400
